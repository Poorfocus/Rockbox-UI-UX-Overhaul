#!/usr/bin/perl

use strict;
use warnings;

# Calculate the highest possible location for an overlay based
# on a reference map file (.refmap)

sub map_scan {
    # The buflib handle table is a few hundred bytes, just before
    # the plugin buffer. We assume it's never more than 1024 bytes.
    # If this assumption is wrong, overlay loading will fail.
    my $max_handle_table_size = 1024;
    my ($map) = @_;
    my $ramstart = -1;
    my $ramsize = -1;
    my $startaddr = -1;
    my $endaddr = -1;

    open(my $map_fh, "<", $map) or die "Could not open map file '$map': $!\n";
    while (my $line = <$map_fh>) {
        $line =~ s/[\r\n]+$//;
        if ($line =~ /^PLUGIN_RAM +0x([0-9a-f]+) +0x([0-9a-f]+)$/i) {
            $ramstart = hex($1);
            $ramsize = hex($2);
        }
        elsif ($line =~ / +0x([0-9a-f]+) +_?plugin_start_addr = \./i) {
            $startaddr = hex($1);
        }
        elsif ($line =~ / +0x([0-9a-f]+) +_?plugin_load_end_addr = \./i) {
            $endaddr = hex($1);
        }
    }
    close($map_fh);

    if ($ramstart < 0 || $ramsize < 0 || $startaddr < 0 || $endaddr < 0
        || $ramstart != $startaddr) {
        die "Could not analyze map file '$map'.\n";
    }

    return $ramstart + $ramsize - $endaddr - $max_handle_table_size;
}

printf "%u", map_scan($ARGV[0]) & ~0xf;
