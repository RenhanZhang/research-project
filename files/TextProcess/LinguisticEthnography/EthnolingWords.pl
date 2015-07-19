#!/usr/bin/perl

# EthnolingWords.pl
#
# Copyright (c) 2009-2011 Rada Mihalcea
#
# Starting with a foreground and a background corpus, it finds the dominant
# unigrams, bigrams, trigrams in the corpus. 
#
# INPUT:    A foreground corpus, a background corpus 
#           For sample input, see 
#             foreground: "DATA/ALL.True.txt"
#             background: "DATA/ALL.False.txt"
#
# OUTPUT:   A list of Ngrams, together with their "dominance" score in the
#           foreground corpus.
#
# CHANGE LOG
#
# Date          Author          Change
# =======================================================================
# 10-21-2011    Rada            initial version
# =======================================================================

use lib '/home/rada/research/LingEthnography';
use Getopt::Long;
use tokenizeE;

# set default options and read command line options
$MINDOMINANCE= 2;   # the minimum threshold to be used for the "dominance"
                    # score of an Ngram, so that the Ngram is considered
$MINFREQUENCY = 10; # the minimum frequency for an Ngram to be considered
$N = 1;             # the N-gram length; by default is 1, meaning we 
                    # look for unigrams
$TARGET = "NONE";    # the target word/phrase  for which the analysis is done; 
                    # if specified, only the lines in the corpus that contain
                    # that word/phrase are considered. By default, there is 
                    # no target word, and the entire corpus is processed

if(scalar(@ARGV) == 0) {
    &displayHelp;
    exit;
}

&getCommandLineOptions(\$foregroundCorpus, \$backgroundCorpus, \$targetWord, \$N,\$MINDOMINANCE,\$MINFREQUENCY);

$FOREGROUND = $foregroundCorpus;
$BACKGROUND = $backgroundCorpus;
$TARGET = $targetWord; 

my %wordsForeground;
my $totalForeground = &countWords($FOREGROUND,$TARGET,\%wordsForeground,$N);
print STDERR "Foreground corpus loaded .... \n";


my %wordsBackground;
my $totalBackground = &countWords($BACKGROUND,$TARGET,\%wordsBackground,$N);
print STDERR "Background corpus loaded .... \n";

#foreach my $word (keys %wordsBackground) {
#    print $word," ",$wordsBackground{$word},"\n";
#}
#exit;

foreach my $word (keys %wordsForeground) {

    if($wordsForeground{$word} < $MINFREQUENCY) {
	next;
    }


    my $dominance = 0;
    if(exists($wordsBackground{$word})) {
	# calculate the dominance score; the counts are normalized with the
	# length of the corpus
	$dominance = ($wordsForeground{$word}/$totalForeground)/($wordsBackground{$word}/$totalBackground);
	# the not-normalized version
        #$dominance = $wordsForeground{$word}/$wordsBackground{$word};
    }
    else {
	$dominance = ($wordsForeground{$word}/$totalForeground)/(1/$totalBackground);
	#not-normalized $dominance = $wordsForeground{$word};
    }
    
    if($dominance >= $MINDOMINANCE) {
	print $word," ",$dominance," ",$wordsForeground{$word}," (/",$totalForeground,") ",$wordsBackground{$word}," (/",$totalBackground,")";
	if(!exists($wordsBackground{$word})) {
	    #print " (present only in foreground)";
	}
	print "\n";
    }
}


 



#======================================================================
# Given a corpus, it counts the number of occurrences for all the ngrams 
# in the corpus. If a target word/phrase is specified, it only considers
# those lines in the corpus that contain that particular word/phrase.
#
# CHANGE LOG
#
# Date          Author          Change
#=======================================================================
# 10-21-2011   Rada            initial version
#=======================================================================


sub countWords {
    my ($FILE, $TARGET, $wordsHashRef, $N) = @_;

    open INFILE, "<$FILE";
    (-r INFILE) || die "Could not open corpus file $FILE\n";
    
    my $totalCount = 0;
    my $endOfPreviousLine = "";

    while(my $readline = <INFILE>) {
	$readline =~ s/\s+/ /g;  # make sure all white spaces are uniform

	$line = $endOfPreviousLine." ".$readline;
	&tokenizeE(\$line);
	my @tokens = split /\s+/, $line;

	# collect the last N-1 tokens from this line, so they can be used 
	# to form Ngrams on the next line. This ensures continuity between
	# lines
	$endOfPreviousLine = "";
	for(my $i = scalar(@tokens) - $N + 1; $i < scalar(@tokens); $i++) {
	    $endOfPreviousLine = $tokens[$i]." ";
	}


	# check if a target word/phrase has been specified
	# if so, continue only if the current line includes that word/phrase
	if($TARGET ne "NONE") {
	    if($readline =~ /(^|\b)$TARGET($|\b)/) {
	    }
	    else {
		next;
	    }
	}

	
	#determine the N-grams
	# do not consider Ngrams that have punctuation inside
	my $hasPunctuation = 0;
	for(my $i=0; $i < scalar(@tokens) - $N + 1; $i++) {

	    if($tokens[$i] =~ /^[[:punct:]]/) {
		next;
	    }
	    $hasPunctuation = 0;

	    my $ngram = lc($tokens[$i]);
	    for(my $j=$i+1; $j < $i+$N && $j < scalar(@tokens); $j++) {
		if($tokens[$j] =~ /^[[:punct:]]/) {
		    $hasPunctuation=1;
		    last;
		}
		$ngram .= "_".lc($tokens[$j]);
	    }
	    if($hasPunctuation == 1) {
		next;
	    }

	    $wordsHashRef->{$ngram}++;
	    $totalCount++;
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
    my ($foregroundCorpusRef,$backgroundCorpusRef,$targetWordRef,$NRef,$MINDOMINANCERef,$MINFREQUENCYRef) = @_;

    # get the options
    GetOptions('help', \&displayHelp,
               'fg=s',$foregroundCorpusRef,
               'bg=s', $backgroundCorpusRef,
               'target=s',$targetWordRef,
               'ngram=i', $NRef,
	       'score=i',$MINDOMINANCERef,
	       'freq=i',$MINFREQUENCYRef);

    if(!defined $$foregroundCorpusRef) {
        print STDERR "Please specify a foreground corpus using the -fg option\n";
        exit;
    }

    if(!defined $$backgroundCorpusRef) {
        print STDERR "Please specify a background corpus using the -bg option\n";
        exit;
    }
    
    if(!defined $$targetWordRef) {
	$$targetWordRef = "NONE";
    }
    $$targetWordRef =~ s/\s+/ /g; # make sure all white spaces are uniform

    if(!defined $$NRef) {
        $$NRef = 1;
    }

     if(!defined $$MINDOMINANCERef) {
        $$MINDOMINANCERef = 2;
    }

     if(!defined $$MINFREQUENCYRef) {
        $$MINFREQUENCYRef = 10;
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
    print STDERR "Usage: EthnolingWords.pl -fg <foregroundCorpus> -bg <backgroundCorpus [-ngram <sizeOfNgrams>] [-min <minimumThreshold>] [-help] \n\n";
    print STDERR "EthnoLing: linguistic etnography for textual corpora\n\n";
    print STDERR "  -fg <foregroundCorpus> the main corpus used for analysis\n";
    print STDERR "  -bg <backgroundCorpus> the corpus used for comparison (representing either the opposite phenomenon from the foregroundCorpus, or a general purpose corpus\n";
    print STDERR "  -ngram <sizeOfNgrams> if present, it indicates the length of the Ngrams to be considered. It has a default value of 1.\n";
    print STDERR "  -score <minimumThreshold> if present, it indicates the minimum threshold acceptable for the dominance score of an Ngram, such that the Ngram is considered. It has a default value of 2.\n";
    print STDERR "  -freq <minimumFrequency> if present, it indicates the minimum frequency acceptable for an Ngram, such that the Ngram is considered. It has a default value of 10.\n";
    print STDERR "  -help if present, it displays this help message\n\n";

}

