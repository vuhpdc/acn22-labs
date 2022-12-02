"""
    This file includes utilities for testing AllReduce results
"""
import os, sys, csv, shutil
from datetime import datetime

def _get_or_create_test_root():
    if not os.path.exists(os.environ['APP_TEST']):
        try:
            os.makedirs(os.environ['APP_TEST'])
        except:
            pass
    return os.environ['APP_TEST']

def _empty_dir(d):
    for f in os.listdir(d):
        p = os.path.join(d, f)
        try:
            shutil.rmtree(p)
        except OSError:
            os.remove(p)

def _get_test_dir(testid):
    return os.path.join(_get_or_create_test_root(), "test-%s" % testid)

def _get_or_create_test_dir(testid):
    d = _get_test_dir(testid)
    if not os.path.exists(d):
        try:
            os.makedirs(d)
        except:
            pass
    return d

def _create_data_file(test_dir, rank, data):
    p = os.path.join(test_dir, "data-rank-%s.csv" % rank)
    with open(p, 'w+') as f:
        c = csv.writer(f)
        c.writerow(data)
        f.flush()

def _Pass(out):
    out.write(" PASS\n")

def _Fail(out, msg, prefix="\t"):
    out.write("%sFAIL: %s" % (prefix, msg))

def _get_timestamp():
    now = datetime.now()
    return '%02d:%02d:%02d.%06d' % (now.hour, now.minute, now.second, now.microsecond)

def _run_test(testid, rank, data, test_fn, read_fn, write_to_file=False, num_fails=4):
    assert num_fails > 0, "num_fails must be a positive integer"
    test_dir = _get_or_create_test_dir(testid)
    if not os.path.exists(test_dir):
        print("Could not find test directory for test-%s. Exiting..." % testid)
        sys.exit()
    with open(os.path.join(test_dir, "result-rank-%s.txt" % rank), 'w') if write_to_file else open(sys.stdout.fileno(), 'w', closefd=False) as out:
        out.write("[+] Running test: %s, rank: %d, ts: %s\n" % (testid, rank, _get_timestamp()))
        out.write("[+] From data files:\n")
        data_files = [f for f in os.listdir(test_dir) if os.path.isfile(os.path.join(test_dir, f)) and f.startswith("data-")]
        data_files.sort()
        if len(data_files) == 0:
            out.write("\tDid not find any data files. Stopping")
        else:
            for df in data_files:
                out.write("\t%s\n" % os.path.join(test_dir, df))
            out.write("[+] Result:")

            accum = [0] * len(data)

            for df in data_files:
                with open(os.path.join(test_dir, df), 'r+') as f:
                    reader = csv.reader(f, delimiter=",")
                    df_data = list(reader)
                    assert len(list(df_data)) == 1, "Expected a single line per csv"
                    if len(df_data[0]) != len(data):
                        return _Fail(out, "data length missmatch with file %s" % os.path.join(test_dir, df))
                    for i, v in enumerate(list(map(read_fn, df_data[0]))):
                        accum[i] = accum[i] + v

            failures = [i for i,v in enumerate(accum) if not test_fn(data[i], v)]

            if len(failures) == 0:
                return _Pass(out)
            else:
                out.write("\n");

            for i, idx in enumerate(failures):
                if i == num_fails:
                    break
                _Fail(out, "Expected %s, got %s, at index %s\n" % (accum[idx], data[idx], idx))

            if len(failures) > num_fails:
                out.write("\t...%d more failures omitted\n" % (len(failures) - num_fails))

### PUBLIC API BELOW

def CreateTestData(testid, rank, data):
    """
    Create a .csv with a worker's data (AllReduce input)

    The created file is found under:
        TEST_ROOT/test-<testid>/data-rank-<rank>.csv

    TEST_ROOT is controlled by os.environ['APP_TEST']
    """
    test_dir = _get_or_create_test_dir(testid)
    data_file = _create_data_file(test_dir, rank, data)

def RunIntTest(testid, rank, data, num_fails=4, std_out=False):
    """
    Run the test specififed by <testid>, on a worker with rank <rank>

    The test will first read all data files for the given <testid>, i.e.
        TEST_ROOT/test-<testid>/data-*.csv
    then it will perform a local (and slow) all-reduce to compute the
    expected result, and finaly it will compare that with <data>

    This test will perform integer comparisson on the the values

    By default, the outcome is written in the file:
        TEST_ROOT/test-<testid>/result-rank-<rank>.txt
    If std_out=True, the stdout of the caller's process is used instead.

    If the test fails, up to num_fails failures will be shown
    """
    def _test_int(a, b):
        return int(a) == int(b)
    return _run_test(testid, rank, data, _test_int, int, not std_out, num_fails)

def RunFloatTest(testid, rank, data, tol=1e-04, num_fails=4, std_out=False):
    """
    Run the test specififed by <testid>, on a worker with rank <rank>

    The test will first read all data files for the given <testid>, i.e.
        TEST_ROOT/test-<testid>/data-*.csv
    then it will perform a local (and slow) all-reduce to compute the
    expected result, and finaly it will compare that with <data>

    This test will perform floating point comparisson on the values,
    which is done with a tolerance controlled by 'tol'
    The default value checks if values are equal up to 4 decimal places

    By default, the outcome is written in the file:
        TEST_ROOT/test-<testid>/result-rank-<rank>.txt
    If std_out=True, the stdout of the caller's process is used instead.

    If the test fails, up to num_fails failures will be shown
    """
    def _test_float(a, b, rel_tol=rel_t, abs_tol=0.0):
        # https://peps.python.org/pep-0485/#proposed-implementation
        return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)
    return _run_test(testid, rank, data, _test_float, float, not std_out, num_fails)