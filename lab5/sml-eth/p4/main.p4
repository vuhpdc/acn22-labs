#include <core.p4>
#include <v1model.p4>
#include "worker_counter.p4"
#include "compute.p4"

typedef bit<9>  sw_port_t;   /*< Switch port */
typedef bit<48> mac_addr_t;  /*< MAC address */
#define MAX_CHUNK_SIZE 1400;
#define MAX_INT_SIZE 64;

header ethernet_t {
  /* TODO: Define me */
  macAddr_t dstAddr;
  macAddr_t srcAddr;
  bit<16> etherType;
}

header sml_t {
  bit<8> chunck_id;
  bit<32> no_of_workers;
  bit<32> chunck_size;
}

//Chunck size is 8 for  now
header chunck_t {
  int<32> val0;
  int<32> val1;
  int<32> val2;
  int<32> val3;
  int<32> val4;
  int<32> val5;
  int<32> val6;
  int<32> val7;
}


struct headers {
  ethernet_t eth;
  sml_t sml;
  chunck_t chk;
}

struct metadata { 
  /* empty */ 
  bit<1> first_last_flag; //Check if bit<32> is needed
}

parser TheParser(packet_in packet,
                 out headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {
  /* TODO: Implement me */
  state start {
        transition parse_ethernet;
    }

    state parse_ethernet { 
        packet.extract(hdr.ethernet);
        transition parse_sml;
    }

    state parse_sml {
        packet.extract(hdr.sml);
        transition chunck_parser;
    }

    state chunck_parser {
      packet.extract(hdr.chk);
      transition accept;
    }
}


control TheChecksumVerification(inout headers hdr, inout metadata meta) {
  apply {
    /* TODO: Implement me (if needed) */
  }
}


control TheIngress(inout headers hdr,
                   inout metadata meta,
                   inout standard_metadata_t standard_metadata) {
                    

  WorkerCounter() wctr;

  apply {

    if (hdr.sml.isValid()) {

      //Atomic execution
      @atomic{
        //worker_counter();
        wctr.apply(hdr, meta);
        //Compute 0
        compute.apply(hdr.chk.val0, hdr, 0, hdr.chk.val0);
        //Compute 1
        compute.apply(hdr.chk.val1, hdr, 1, hdr.chk.val1);
        //Compute 2
        compute.apply(hdr.chk.val2, hdr, 2, hdr.chk.val2);
        //Compute 3
        compute.apply(hdr.chk.val3, hdr, 3, hdr.chk.val3);
        //Compute 4
        compute.apply(hdr.chk.val4, hdr, 4, hdr.chk.val4);
        //Compute 5
        compute.apply(hdr.chk.val5, hdr, 5, hdr.chk.val5);
        //Compute 6
        compute.apply(hdr.chk.val6, hdr, 6, hdr.chk.val6);
        //Compute 7
        compute.apply(hdr.chk.val7, hdr, 7, hdr.chk.val7);
      }
      //End of atomic execution

      
    }
    //End of if

  }
  //End of apply
}

control TheEgress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {
  apply {
    /* TODO: Implement me (if needed) */
  }
}

control TheChecksumComputation(inout headers  hdr, inout metadata meta) {
  apply {
    /* TODO: Implement me (if needed) */
  }
}

control TheDeparser(packet_out packet, in headers hdr) {
  apply {
    /* TODO: Implement me */
  }
}

V1Switch(
  TheParser(),
  TheChecksumVerification(),
  TheIngress(),
  TheEgress(),
  TheChecksumComputation(),
  TheDeparser()
) main;