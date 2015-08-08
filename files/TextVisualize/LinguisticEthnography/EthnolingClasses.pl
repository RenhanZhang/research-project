#!/usr/bin/perl

# EthnolingClasses.pl
#
# Copyright (c) 2009-2011 Rada Mihalcea
#
# Starting with a foreground and a background corpus, and a list of words
# mapped to categories, it finds the dominant classes in the foreground
# corpus. It uses the method proposed in (Mihalcea and Pulman, 2009)
#
# INPUT:    A foreground corpus, a background corpus, a dictionary file
#           For sample input, see 
#             foreground: "DATA/ALL.True.txt"
#             background: "DATA/ALL.False.txt"
#             dictionary: "LIWC/LIWC.all.txt"
#              other dictionaries: "WordNetAffect/WordNetAffect.all.txt"
#                                  "Roget/Roget.all.txt"
#
# OUTPUT:   A list of classes, together with their "dominance" score in the
#           foreground corpus.
#
# CHANGE LOG
#
# Date          Author          Change
# =======================================================================
# 10-21-2011    Rada            code revised for added flexibility 
# 10-20-2009    Rada            initial version
# =======================================================================
use lib '/Users/rhzhang/Desktop/LinguisticEthnography';

use Getopt::Long;
use tokenizeE;

# set default options and read command line options

$WILDCARD = 1;     # flag 1/0 - use/not use the wildcard in the matches
                   # LIWC does use a wildcard; other resources do not
$MINTHRESHOLD = 2;# need at least this many words in a class, for the
                   # class to be considered
$MINLENGTH = 0;    # the minimum number of characters in a word
                   # for the word to be included in the dictionary
$EXPLAIN = 0;      # flag 1/0 - show/do not show the words that make up 
                   # a certain class in a corpus, together with their counts
                   # by default it is 0

if(scalar(@ARGV) == 0) {
    &displayHelp;
    exit;
}

&getCommandLineOptions(\$foregroundCorpus, \$backgroundCorpus, \$dictionary,\$MINTHRESHOLD,\$EXPLAIN);

$FOREGROUND = $foregroundCorpus;
$BACKGROUND = $backgroundCorpus;
$DICTIONARY = $dictionary;


my %dictionary;
&loadDictionary($DICTIONARY,\%dictionary);
print STDERR "Dictionary loaded .... \n";

my %classesForeground;
my $totalForeground = &countClassWords($FOREGROUND,\%dictionary,\%classesForeground);
print STDERR "Foreground corpus loaded .... \n";


my %classesBackground;
my $totalBackground = &countClassWords($BACKGROUND,\%dictionary,\%classesBackground);
print STDERR "Background corpus loaded .... \n";

foreach my $class (keys %classesForeground) {
    if($classesForeground{$class}{totalCount} < $MINTHRESHOLD) {
	$classesForeground{$class}{totalCount} = 0;
    }
    $classesForeground{$class}{totalCount} /= $totalForeground;
}

foreach my $class (keys %classesBackground) {
    if($classesBackground{$class}{totalCount} < $MINTHRESHOLD) {
	$classesBackground{$class}{totalCount} = 0;
    }
    $classesBackground{$class}{totalCount} /= $totalBackground;
}

# display the dominance score, calculated as the fraction of 
# foreground class score divided by the background class score
# if the class is missing from the background, a score of 1 is
# assumed for the background
foreach my $class (keys %classesForeground) {
    if($classesForeground{$class}{totalCount} == 0) {
	next;
    }
    if($classesBackground{$class}{totalCount} != 0) {
	print $class," ",$classesForeground{$class}{totalCount}/$classesBackground{$class}{totalCount}," ";
    }
    else {
	print $class, " ",$classesForeground{$class}{totalCount}," (Not present in background) ";
    }
    if($EXPLAIN == 1) {
	foreach my $token (keys %{$classesForeground{$class}}) {
	    if($token ne totalCount) {
		print $token,"(",$classesForeground{$class}{lc($token)},") ";
	    }
	}
    }
    print "\n";
}



 

#======================================================================
# Load the dictionary into a hash. The dictionary is a raw text file,
# with lines following this format:
#
#    word,CLASS
#
# Note that a word can belong to more than one class. Also, words can
# optionally include a wildcard, to maximize the chance of a match between
# the dictionary word and the corpus. The wildcard will be preserved if
# present.
#
# CHANGE LOG
#
# Date          Author          Change
#=======================================================================
# 10-21-2009   Rada            initial version
#=======================================================================


sub loadDictionary {
    my ($FILE, $hashRef) = @_;

    open INFILE, "<$FILE";
    (-r INFILE) || die "Could not open dictionary file $FILE\n";
    
    while(my $line = <INFILE>) {
	chomp $line;
	my ($word, $class) = split /\,/, $line;
	
	$word =~ s/^\s+//; $word =~ s/\s+$//;
	if(length($word) <= $MINLENGTH) {
	    next;
	}

	$class =~ s/^\s+//; $class =~ s/\s+$//;
	$class =~ s/\s+/_/g;

	# add the class to the hash entry for this word
	# NB!! a word can belong to several classes
	$hashRef->{lc($word)} .= " ".$class;
    }

    # print the dictionary
    #foreach my $key (keys %$hashRef) {
    #	print $key," ",$hashRef->{$key},"\n";
    #}

    close INFILE;
}


#======================================================================
# Given a corpus and a dictionary loaded into a hash, it counts the 
# number of words in the corpus for each class. It updates a class hash
# with the number of words found for that particular class.
#
# CHANGE LOG
#
# Date          Author          Change
#=======================================================================
# 10-21-2009   Rada            initial version
#=======================================================================


sub countClassWords {
    my ($FILE, $dictHashRef, $classHashRef) = @_;

    open INFILE, "<$FILE";
    (-r INFILE) || die "Could not open corpus file $FILE\n";
    
    my $totalCount = 0;

    # manual exclusion of terms not to be included
#%exclude = qw(firms 1 tiered 1 firman 1 diving 1 sickday 1 allergies 1 graceland 1 careful 1 carey 1 dearborn 1 deartony 1 gentleman 1 gentlemen 1 graceland 1 hearth 1 heartily 1 heartland 1 hearty 1 humaniods 1 meaning 1 means 1 meantime 1 humans 1 career 1 careers 1 meanings 1 meant 1 paint 1 painted 1 paints 1 painter 1 painting 1 several 1 severed 1 tactics 1 tactical 1  hand 1 handler 1 handsets 1 handing 1 handy 1 handed 1 handfuls 1 handicap 1 couple 1 coupled 1 couples 1 coupon 1 couponer 1 coupo 1 coupons 1 warranty 1 followup 1 fairfax 1 lawn 1 recipe 1 recipes 1 lawdy 1 lawd 1 fairtra 1 recipies 1 fairtrad 1 lawnt 1 fairtade 1 fairtr 1 fairy 1 fairys 1 lawry 1 lawrys 1 lawan 1);


    while(my $line = <INFILE>) {
	&tokenizeE(\$line);

	my @tokens = split /\s+/, $line;


	## TODO -- maybe: need to take care of multiple word matches
	foreach my $token (@tokens) {
	    $totalCount++;
	    my $classes = "";

	    
	    if(exists($exclude{$token})) {next;}

	
	    # first look for the entire $token
	    if(exists($dictHashRef->{lc($token)})) {
		$classes =  $dictHashRef->{lc($token)};
	    }

	    # if the entire token was not found, check if the
	    # presence of wildcards is possible in this dictionary
	    # and if so, try to do a wildcard match
	    else {
		# if the wildcard can be used in word matches
		if(1 == $WILDCARD) {
		    my $len = length($token);
		    # if the entire token was not found, look for subtokens 
		    # with a * ending -- this is relevant for LIWC only
		    for(my $i=0; $i < 5 && $i < $len; $i++) {
			if($classes ne "") {
			    last;
			}
			my $subtoken = substr($token,0,$len-$i);
			if(exists($dictHashRef->{lc($subtoken."*")})) {
			    $classes =  $dictHashRef->{lc($subtoken."*")};
			}
		    }
		}
		
	    }
	    if($classes ne "") { 
		$classes =~ s/^\s+//;
		my @classes = split /\s+/, $classes;
		foreach my $class (@classes) {
		    $classHashRef->{$class}{totalCount}++;
		    $classHashRef->{$class}{lc($token)}++;
		}
	    }
	}
    }


   
    close INFILE;
    return $totalCount;
}


#=======================================================================
# getCommandLineOptions
#
# Get the command lines options
# Check existence/validity of mandatory options
#
# CHANGE LOG
#
# Date          Author          Change
#=======================================================================
# 10-21-2011    Rada            initial version
#=======================================================================

sub getCommandLineOptions {
    my ($foregroundCorpusRef,$backgroundCorpusRef,$dictionaryRef,$thresholdRef,$explainRef) = @_;

    # get the options
    GetOptions('help', \&displayHelp,
               'fg=s',$foregroundCorpusRef,
               'bg=s', $backgroundCorpusRef,
               'dict=s', $dictionaryRef,
	       'explain',$explainRef);

    if(!defined $$foregroundCorpusRef) {
        print STDERR "Please specify a foreground corpus using the -fg option\n";
        exit;
    }

    if(!defined $$backgroundCorpusRef) {
        print STDERR "Please specify a background corpus using the -bg option\n";
        exit;
    }

    if(!defined $$dictionaryRef) {
        print STDERR "Please specify a dictionary file, using the -dict option\n";
        exit;
    }

    if(!defined $$thresholdRef) {
        $$thresholdRef = 2;
    }


}





#=================================================================
# displayHelp
#
# prints out the help message, including usage
#
# CHANGE LOG
#
# Date          Author          Change
# ========================================================================
# 10-21-2011    Rada            Initial version
# ========================================================================
sub displayHelp()
{
    print STDERR "Usage: findWordClasses.pl -fg <foregroundCorpus> -bg <backgroundCorpus -dict <dictionaryFile> [-explain] [-help] \n\n";
    print STDERR "EthnoLing: linguistic etnography for textual corpora\n";
    print STDERR "  -fg <foregroundCorpus> the main corpus used for analysis\n";
    print STDERR "  -bg <backgroundCorpus> the corpus used for comparison (representing either the opposite phenomenon from the foregroundCorpus, or a general purpose corpus\n";
    print STDERR "  -dict <dictionaryFile> the file containing the dictionary of classes. Each line in this file should have the format: word CLASS\n";
    print STDERR "  -threshold <number> if present, it specifies the minimum number of words in a class for the class to be considered. The default value is 2.\n";
    print STDERR "  -explain if present, it also shows the words found in the foreground corpus belonging to every single class\n"; 
    print STDERR "  -help if present, it displays this help message\n";
}

