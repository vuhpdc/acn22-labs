control WorkerCounter(in headers hdr, inout metadata meta) {
    //Define register
    Register<bit<32>,bit<1>>(1) Counter;

    //Define Register Action
    RegisterAction<bit<32>, bit<1>, bit<32>>(Counter) workers_count_action = {
        void apply(inout bit<32> value, out bit<32> read_value) {
            read_value = value; //Storing value before updating to get flag. 0 is first and 1 is last
            if (value == 0) {
                value = hdr.sml.no_of_workers - 1;
            } else {
                value = value - 1;
            }
        }
    };

    apply {
        meta.first_last_flag = workers_count_action.execute(0);
    }
}