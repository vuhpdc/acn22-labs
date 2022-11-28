#include <core.p4>
#include <v1model.p4>

typedef bit<9>  sw_port_t;   /*< Switch port */
typedef bit<48> mac_addr_t;  /*< MAC address */
typedef bit<32> ip4_addr_t;  /*< IPv4 address */

header ethernet_t {
  /* TODO: Define me */
}

header ipv4_t {
  /* TODO: Define me */
}

header udp_t {
  /* TODO: Define me */
}

header sml_t {
  /* TODO: Define me */
}

struct headers {
  ethernet_t eth;
  ipv4_t ipv4;
  udp_t udp;
  sml_t sml;
}

struct metadata { /* empty */ }

parser TheParser(packet_in packet,
                 out headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {
  /* TODO: Implement me */
  state start {}
}

control TheIngress(inout headers hdr,
                   inout metadata meta,
                   inout standard_metadata_t standard_metadata) {
  apply {
    /* TODO: Implement me */
  }
}

control TheEgress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {
  apply {
    /* TODO: Implement me (if needed) */
  }
}

control TheChecksumVerification(inout headers hdr, inout metadata meta) {
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