control compute(in int<32> inval, in headers hdr, in bit<32> index, out int<32> outval) {

    //Define register
    Register<int<32>,bit<1>>(1) CHK;

    //Define Register actions
    RegisterAction<int<32>, bit<1>, int<32>>(CHK) aggregateNread = {
        void apply(inout int<32> value, out int<32> read_value) {
            value = value + inval;
            read_value = value;
        }
    };

    RegisterAction<int<32>, bit<1>, int<32>>(CHK) init = {
        void apply(inout int<32> value, out int<32> read_value) {
            value = inval;
        }
    };

    apply {
        //Check if this chunck index is valid
        if(index < hdr.sml.chunck_size) {
            //Check meta.first_last_flag
            if(meta.first_last_flag == 0) {
                init.execute(0);
            } else {
                outval = aggregateNread.execute(0);
            }
        }
    }
}