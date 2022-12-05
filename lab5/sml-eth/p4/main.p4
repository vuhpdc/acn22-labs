#include <core.p4>
#include <v1model.p4>

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
  bit<64> no_of_workers;
  bit<64> chunck_size;
  int<64>[MAX_CHUNCK_SIZE] chunck; //Array of max size MAX_CHUNK_SIZE
}

struct headers {
  ethernet_t eth;
  sml_t sml;
}

struct metadata { /* empty */ }

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
        transition select(hdr.ethernet.etherType) {
            0x0: parse_sml; //Provide ether type for custom
            default: accept;
        }
    }

    state parse_sml {
        packet.extract(hdr.sml);
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
  //Define two registers
  //Vector
  register<int<64>>(MAX_CHUNK_SIZE) vector;
  //Count
  register<bit<64>>(1) count;
  bit<64> count_loader;
  
  action compute(bit<64> chunck_size, int<64>[MAX_CHUNCK_SIZE] chunck) { 
    //Parameters chunck and chunck_size;
    int<64> vector_pos_val;
    //No loops in p4
    for(int i = 0; i < chunck_size; i++) { 
      vector.read(vector_pos_val, i);
      vector_pos_val = vector_pos_val + chunck[i]; 
      vector.write(i, vector_pos_val); //TODO: Change to write and read of register operation
    }
    count += 1; //TODO: Change to write and read of register operation
  }

  action send_results() {
    //No parameters needed
    //Get vector from registers and set it to multicast it to all
    //Reset vector and count to 0
  }

  apply {
    /* TODO: Implement me */
    if (hdr.sml.isValid()) {
      compute(hdr.sml.chunck_size, hdr.sml.chunck);
      count.read(count_loader, 1);
      if (count_loader == hdr.sml.no_of_workers) {
        send_results();
      }
    }
  }
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