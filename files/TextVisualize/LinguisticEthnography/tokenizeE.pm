#!/usr/bin/perl -w
# -*- perl -*-

###########################################################################
# This is a tokenizer for English. It was written as a single perl script #
#      by Yaser Al-Onaizan based on several scripts by Dan Melamed.       #
#  WS'99 STatistical Machine Translation Team.                            #     
#  IN: Englsih text in                                                    #
#  OUT: tokenized English text                                            #
#  Usage: $tokenize(\$text);
###########################################################################     

sub tokenizeE {
     
    my ($pLine) = @_;
    my $line = $$pLine;

    # make sure empty lines stay in
    if($line =~ /^\s+$/) {
	$$_[0] = $line;
	return;
    }
	
    &Estem_contractions(\$line);
    &Edelimit_tokens(\$line);
    &Estem_elision(\$line);
	
    # RADA  - for English data in Ro-En
    $line =~ s/([\"\'\`])/ $1 /g; #separates the quotes, if any left.
    $line =~ s/\s+\'\s+s\s+/ \'s /g;  #put back the appositive 's
    $line =~ s/\s+\'\s+re\s+/ \'re /g; #put back the verb are form
    $line =~ s/n\s+\'\s+t\s+/n\'t /g;  #put back the negated form 
	
    &Emerge_abbr(\$line);
    $line =~ tr/[ \t\r\n]//s; # supress multiple white spaces into single space
    $line =~ s/^\s+//;

    $$pLine = $line;
}




sub Estem_contractions{

    my ($pLine) = @_;
    my $line = $$pLine;
    

    $line =~ s/\'t/\'t/g;
    $line =~ s/\'m/\'m/g;
    $line =~ s/\'re/\'re/g;
    $line =~ s/\'ll/\'ll/g;
    $line =~ s/\'ve/\'ve/g;
# put space before ambiguous contractions
    $line =~ s/([^ ])\'s/$1 \'s/g;
    $line =~ s/([^ ])\'d/$1 \'d/g;    

    $$pLine = $line;

}


sub Estem_elision{
# stems English elisions, except for the ambiguous cases of 's and 'd

    my ($pLine) = @_;
    my $line = $$pLine;
    

    $line =~ s/Won \'t/Won* n\'t/g;
    $line =~ s/Can \'t/Can* n\'t/g;
    $line =~ s/Shan \'t/Shan* n\'t/g;
    $line =~ s/won \'t/won* n\'t/g;
    $line =~ s/can \'t/can* n\'t/g;
    $line =~ s/shan \'t/shan* n\'t/g;
    $line =~ s/n 't/ n't/g;
# s/ 'm/ am/g;
# s/n 't/ not/g;
# s/ 're/ are/g;
# s/ 'll/ will/g;
# s/ 've/ have/g;

    $$pLine = $line;


}

sub Edelimit_tokens{

    my ($pLine) = @_;
    my $line = $$pLine;
   
# puts spaces around punctuation and special symbols

# stardardize quotes
    $line =~ s/\'\' /\" /g;
    $line =~ s/ \`\`/ \"/g;
    $line =~ s/\'\'$/\"/g;
    $line =~ s/^\`\`/\"/g;
    
# put space after any period that's followed by a non-number and non-period
    $line =~ s/\.([^0-9\.])/\. $1/g;
    $line =~ s/\.$/\. /g;
# put space before any period that's followed by a space or another period, 
# unless preceded by another period
# the following space is introduced in the previous command
    $line =~ s/([^\.])\.([ \.])/$1 \.$2/g;
    
# put space around sequences of colons and comas, unless they're
# surrounded by numbers or other colons and comas
    $line =~ s/([0-9:])\:([0-9:])/$1<CLTKN>$2/g;
    $line =~ s/\:/ \: /g;
    $line =~ s/([0-9]) ?<CLTKN> ?([0-9])/$1\:$2/g;
    $line =~ s/([0-9,])\,([0-9,])/$1<CMTKN>$2/g;
    $line =~ s/\,/ \, /g;
    $line =~ s/([0-9]) ?<CMTKN> ?([0-9])/$1\,$2/g;
    
# put space before any other punctuation and special symbol sequences
    $line =~ s/([^ \!])(\!+)/$1 $2/g;
    $line =~ s/([^ \?])(\?+)/$1 $2/g;
    $line =~ s/([^ \;])(\;+)/$1 $2/g;
    $line =~ s/([^ \"])(\"+)/$1 $2/g;
    $line =~ s/([^ \)])(\)+)/$1 $2/g;
    $line =~ s/([^ \(])(\(+)/$1 $2/g;
    $line =~ s/([^ \/])(\/+)/$1 $2/g;
    $line =~ s/([^ \&])(\&+)/$1 $2/g;
    $line =~ s/([^ \^])(\^+)/$1 $2/g;
    $line =~ s/([^ \%])(\%+)/$1 $2/g;
    $line =~ s/([^ \$])(\$+)/$1 $2/g;
    $line =~ s/([^ \+])(\++)/$1 $2/g;
    $line =~ s/([^ \-])(\-+)/$1 $2/g;
    $line =~ s/([^ \#])(\#+)/$1 $2/g;
    $line =~ s/([^ \*])(\*+)/$1 $2/g;
    $line =~ s/([^ \[])(\[+)/$1 $2/g;
    $line =~ s/([^ \]])(\]+)/$1 $2/g;
    $line =~ s/([^ \{])(\{+)/$1 $2/g;
    $line =~ s/([^ \}])(\}+)/$1 $2/g;
    $line =~ s/([^ \>])(\>+)/$1 $2/g;
    $line =~ s/([^ \<])(\<+)/$1 $2/g;
    $line =~ s/([^ \_])(\_+)/$1 $2/g;
    $line =~ s/([^ \\])(\\+)/$1 $2/g;
    $line =~ s/([^ \|])(\|+)/$1 $2/g;
    $line =~ s/([^ \=])(\=+)/$1 $2/g;
    $line =~ s/([^ \'])(\'+)/$1 $2/g;
    $line =~ s/([^ \`])(\`+)/$1 $2/g;
    
    $line =~ s/([^ \²])(\²+)/$1 $2/g;
    $line =~ s/([^ \³])(\³+)/$1 $2/g;
    $line =~ s/([^ \«])(\«+)/$1 $2/g;
    $line =~ s/([^ \»])(\»+)/$1 $2/g;
    $line =~ s/([^ \¢])(\¢+)/$1 $2/g;
    $line =~ s/([^ \°])(\°+)/$1 $2/g;
    
# put space after any other punctuation and special symbols sequences
    $line =~ s/(\!+)([^ \!])/$1 $2/g;
    $line =~ s/(\?+)([^ \?])/$1 $2/g;
    $line =~ s/(\;+)([^ \;])/$1 $2/g;
    $line =~ s/(\"+)([^ \"])/$1 $2/g;
    $line =~ s/(\(+)([^ \(])/$1 $2/g;
    $line =~ s/(\)+)([^ \)])/$1 $2/g;
    $line =~ s/(\/+)([^ \/])/$1 $2/g;
    $line =~ s/(\&+)([^ \&])/$1 $2/g;
    $line =~ s/(\^+)([^ \^])/$1 $2/g;
    $line =~ s/(\%+)([^ \%])/$1 $2/g;
    $line =~ s/(\$+)([^ \$])/$1 $2/g;
    $line =~ s/(\++)([^ \+])/$1 $2/g;
    $line =~ s/(\-+)([^ \-])/$1 $2/g;
    $line =~ s/(\#+)([^ \#])/$1 $2/g;
    $line =~ s/(\*+)([^ \*])/$1 $2/g;
    $line =~ s/(\[+)([^ \[])/$1 $2/g;
    $line =~ s/(\]+)([^ \]])/$1 $2/g;
    $line =~ s/(\}+)([^ \}])/$1 $2/g;
    $line =~ s/(\{+)([^ \{])/$1 $2/g;
    $line =~ s/(\\+)([^ \\])/$1 $2/g;
    $line =~ s/(\|+)([^ \|])/$1 $2/g;
    $line =~ s/(\_+)([^ \_])/$1 $2/g;
    $line =~ s/(\<+)([^ \<])/$1 $2/g;
    $line =~ s/(\>+)([^ \>])/$1 $2/g;
    $line =~ s/(\=+)([^ \=])/$1 $2/g;
    $line =~ s/(\`+)([^ \`])/$1 $2/g;
# $line =~ s/(\'+)([^ \'])/$1 $2/g;      # do not insert space after forward tic

    $line =~ s/(\²+)([^ \²])/$1 $2/g;
    $line =~ s/(\³+)([^ \³])/$1 $2/g;
    $line =~ s/(\«+)([^ \«])/$1 $2/g;
    $line =~ s/(\»+)([^ \»])/$1 $2/g;
    $line =~ s/(\¢+)([^ \¢])/$1 $2/g;
    $line =~ s/(\°+)([^ \°])/$1 $2/g;

# separate alphabetical tokens

    $line =~ s/([a-zA-Z]+)/ $1 /g;    

    $$pLine = $line;


}


sub Emerge_abbr(){

    my ($pLine) = @_;
    my $line = $$pLine;

    $line =~ s/[\s\.]U\s+\.\s+S\s+\.\s+S\s+\.\s+R\s+\./U.S.S.R./g;
    $line =~ s/[\s\.]U\s+\.\s+S\s+\.\s+A\s+\./U.S.A./g;
    $line =~ s/[\s\.]P\s+\.\s+E\s+\.\s+I\s+\./P.E.I./g;
    $line =~ s/[\s\.]p\s+\.\s+m\s+\./p.m./g;
    $line =~ s/[\s\.]a\s+\.\s+m\s+\./a.m./g;
    $line =~ s/[\s\.]U\s+\.\s+S\s+\./U.S./g;
    $line =~ s/[\s\.]B\s+\.\s+C\s+\./B.C./g;
    $line =~ s/[\s\.]vol\s+\./vol./g;
    $line =~ s/[\s\.]viz\s+\./viz./g;
    $line =~ s/[\s\.]v\s+\./v./g;
    $line =~ s/[\s\.]terr\s+\./terr./g;
    $line =~ s/[\s\.]tel\s+\./tel./g;
    $line =~ s/[\s\.]subss\s+\./subss./g;
    $line =~ s/[\s\.]subs\s+\./subs./g;
    $line =~ s/[\s\.]sub\s+\./sub./g;
    $line =~ s/[\s\.]sess\s+\./sess./g;
    $line =~ s/[\s\.]seq\s+\./seq./g;
    $line =~ s/[\s\.]sec\s+\./sec./g;
    $line =~ s/[\s\.]rév\s+\./rév./g;
    $line =~ s/[\s\.]rev\s+\./rev./g;
    $line =~ s/[\s\.]repl\s+\./repl./g;
    $line =~ s/[\s\.]rep\s+\./rep./g;
    $line =~ s/[\s\.]rel\s+\./rel./g;
    $line =~ s/[\s\.]paras\s+\./paras./g;
    $line =~ s/[\s\.]para\s+\./para./g;
    $line =~ s/[\s\.]op\s+\./op./g;
    $line =~ s/[\s\.]nom\s+\./nom./g;
    $line =~ s/[\s\.]nil\s+\./nil./g;
    $line =~ s/[\s\.]mr\s+\./mr./g;
    $line =~ s/[\s\.]lég\s+\./lég./g;
    $line =~ s/[\s\.]loc\s+\./loc./g;
    $line =~ s/[\s\.]jur\s+\./jur./g;
    $line =~ s/[\s\.]int\s+\./int./g;
    $line =~ s/[\s\.]incl\s+\./incl./g;
    $line =~ s/[\s\.]inc\s+\./inc./g;
    $line =~ s/[\s\.]id\s+\./id./g;
    $line =~ s/[\s\.]ibid\s+\./ibid./g;
    $line =~ s/[\s\.]hum\s+\./hum./g;
    $line =~ s/[\s\.]hon\s+\./hon./g;
    $line =~ s/[\s\.]gén\s+\./gén./g;
    $line =~ s/[\s\.]etc\s+\./etc./g;
    $line =~ s/[\s\.]esp\s+\./esp./g;
    $line =~ s/[\s\.]eg\s+\./eg./g;
    $line =~ s/[\s\.]eds\s+\./eds./g;
    $line =~ s/[\s\.]ed\s+\./ed./g;
    $line =~ s/[\s\.]crit\s+\./crit./g;
    $line =~ s/[\s\.]corp\s+\./corp./g;
    $line =~ s/[\s\.]conf\s+\./conf./g;
    $line =~ s/[\s\.]comp\s+\./comp./g;
    $line =~ s/[\s\.]comm\s+\./comm./g;
    $line =~ s/[\s\.]com\s+\./com./g;
    $line =~ s/[\s\.]co\s+\./co./g;
    $line =~ s/[\s\.]civ\s+\./civ./g;
    $line =~ s/[\s\.]cit\s+\./cit./g;
    $line =~ s/[\s\.]chap\s+\./chap./g;
    $line =~ s/[\s\.]cert\s+\./cert./g;
    $line =~ s/[\s\.]ass\s+\./ass./g;
    $line =~ s/[\s\.]arts\s+\./arts./g;
    $line =~ s/[\s\.]art\s+\./art./g;
    $line =~ s/[\s\.]alta\s+\./alta./g;
    $line =~ s/[\s\.]al\s+\./al./g;
    $line =~ s/[\s\.]Yes\s+\./Yes./g;
    $line =~ s/[\s\.]XX\s+\./XX./g;
    $line =~ s/[\s\.]XVIII\s+\./XVIII./g;
    $line =~ s/[\s\.]XVII\s+\./XVII./g;
    $line =~ s/[\s\.]XVI\s+\./XVI./g;
    $line =~ s/[\s\.]XV\s+\./XV./g;
    $line =~ s/[\s\.]XIX\s+\./XIX./g;
    $line =~ s/[\s\.]XIV\s+\./XIV./g;
    $line =~ s/[\s\.]XIII\s+\./XIII./g;
    $line =~ s/[\s\.]XII\s+\./XII./g;
    $line =~ s/[\s\.]XI\s+\./XI./g;
    $line =~ s/[\s\.]X\s+\./X./g;
    $line =~ s/[\s\.]Wash\s+\./Wash./g;
    $line =~ s/[\s\.]Vol\s+\./Vol./g;
    $line =~ s/[\s\.]Vict\s+\./Vict./g;
    $line =~ s/[\s\.]Ves\s+\./Ves./g;
    $line =~ s/[\s\.]Va\s+\./Va./g;
    $line =~ s/[\s\.]VIII\s+\./VIII./g;
    $line =~ s/[\s\.]VII\s+\./VII./g;
    $line =~ s/[\s\.]VI\s+\./VI./g;
    $line =~ s/[\s\.]V\s+\./V./g;
    $line =~ s/[\s\.]Univ\s+\./Univ./g;
    $line =~ s/[\s\.]Trib\s+\./Trib./g;
    $line =~ s/[\s\.]Tr\s+\./Tr./g;
    $line =~ s/[\s\.]Tex\s+\./Tex./g;
    $line =~ s/[\s\.]Surr\s+\./Surr./g;
    $line =~ s/[\s\.]Supp\s+\./Supp./g;
    $line =~ s/[\s\.]Sup\s+\./Sup./g;
    $line =~ s/[\s\.]Stud\s+\./Stud./g;
    $line =~ s/[\s\.]Ste\s+\./Ste./g;
    $line =~ s/[\s\.]Stat\s+\./Stat./g;
    $line =~ s/[\s\.]Stan\s+\./Stan./g;
    $line =~ s/[\s\.]St\s+\./St./g;
    $line =~ s/[\s\.]Soc\s+\./Soc./g;
    $line =~ s/[\s\.]Sgt\s+\./Sgt./g;
    $line =~ s/[\s\.]Sess\s+\./Sess./g;
    $line =~ s/[\s\.]Sept\s+\./Sept./g;
    $line =~ s/[\s\.]Sch\s+\./Sch./g;
    $line =~ s/[\s\.]Sask\s+\./Sask./g;
    $line =~ s/[\s\.]ST\s+\./ST./g;
    $line =~ s/[\s\.]Ry\s+\./Ry./g;
    $line =~ s/[\s\.]Rev\s+\./Rev./g;
    $line =~ s/[\s\.]Rep\s+\./Rep./g;
    $line =~ s/[\s\.]Reg\s+\./Reg./g;
    $line =~ s/[\s\.]Ref\s+\./Ref./g;
    $line =~ s/[\s\.]Qué\s+\./Qué./g;
    $line =~ s/[\s\.]Que\s+\./Que./g;
    $line =~ s/[\s\.]Pub\s+\./Pub./g;
    $line =~ s/[\s\.]Pty\s+\./Pty./g;
    $line =~ s/[\s\.]Prov\s+\./Prov./g;
    $line =~ s/[\s\.]Prop\s+\./Prop./g;
    $line =~ s/[\s\.]Prof\s+\./Prof./g;
    $line =~ s/[\s\.]Probs\s+\./Probs./g;
    $line =~ s/[\s\.]Plc\s+\./Plc./g;
    $line =~ s/[\s\.]Pas\s+\./Pas./g;
    $line =~ s/[\s\.]Parl\s+\./Parl./g;
    $line =~ s/[\s\.]Pa\s+\./Pa./g;
    $line =~ s/[\s\.]Oxf\s+\./Oxf./g;
    $line =~ s/[\s\.]Ont\s+\./Ont./g;
    $line =~ s/[\s\.]Okla\s+\./Okla./g;
    $line =~ s/[\s\.]Nw\s+\./Nw./g;
    $line =~ s/[\s\.]Nos\s+\./Nos./g;
    $line =~ s/[\s\.]No\s+\./No./g;
    $line =~ s/[\s\.]Nfld\s+\./Nfld./g;
    $line =~ s/[\s\.]NOC\s+\./NOC./g;
    $line =~ s/[\s\.]Mut\s+\./Mut./g;
    $line =~ s/[\s\.]Mtl\s+\./Mtl./g;
    $line =~ s/[\s\.]Ms\s+\./Ms./g;
    $line =~ s/[\s\.]Mrs\s+\./Mrs./g;
    $line =~ s/[\s\.]Mr\s+\./Mr./g;
    $line =~ s/[\s\.]Mod\s+\./Mod./g;
    $line =~ s/[\s\.]Minn\s+\./Minn./g;
    $line =~ s/[\s\.]Mich\s+\./Mich./g;
    $line =~ s/[\s\.]Mgr\s+\./Mgr./g;
    $line =~ s/[\s\.]Mfg\s+\./Mfg./g;
    $line =~ s/[\s\.]Messrs\s+\./Messrs./g;
    $line =~ s/[\s\.]Mass\s+\./Mass./g;
    $line =~ s/[\s\.]Mar\s+\./Mar./g;
    $line =~ s/[\s\.]Man\s+\./Man./g;
    $line =~ s/[\s\.]Maj\s+\./Maj./g;
    $line =~ s/[\s\.]MURRAY\s+\./MURRAY./g;
    $line =~ s/[\s\.]MR\s+\./MR./g;
    $line =~ s/[\s\.]M\s+\./M./g;
    $line =~ s/[\s\.]Ltd\s+\./Ltd./g;
    $line =~ s/[\s\.]Ll\s+\./Ll./g;
    $line =~ s/[\s\.]Ld\s+\./Ld./g;
    $line =~ s/[\s\.]LTD\s+\./LTD./g;
    $line =~ s/[\s\.]Jun\s+\./Jun./g;
    $line =~ s/[\s\.]Jr\s+\./Jr./g;
    $line =~ s/[\s\.]JJ\s+\./JJ./g;
    $line =~ s/[\s\.]JA\s+\./JA./g;
    $line =~ s/[\s\.]Ir\s+\./Ir./g;
    $line =~ s/[\s\.]Int\s+\./Int./g;
    $line =~ s/[\s\.]Inst\s+\./Inst./g;
    $line =~ s/[\s\.]Ins\s+\./Ins./g;
    $line =~ s/[\s\.]Inc\s+\./Inc./g;
    $line =~ s/[\s\.]Imm\s+\./Imm./g;
$line =~ s/[\s\.]Ill\s+\./Ill./g;
$line =~ s/[\s\.]IX\s+\./IX./g;
$line =~ s/[\s\.]IV\s+\./IV./g;
$line =~ s/[\s\.]INC\s+\./INC./g;
$line =~ s/[\s\.]III\s+\./III./g;
$line =~ s/[\s\.]II\s+\./II./g;
$line =~ s/[\s\.]I\s+\./I./g;
$line =~ s/[\s\.]Hum\s+\./Hum./g;
$line =~ s/[\s\.]Hon\s+\./Hon./g;
$line =~ s/[\s\.]Harv\s+\./Harv./g;
$line =~ s/[\s\.]Hagg\s+\./Hagg./g;
$line =~ s/[\s\.]HON\s+\./HON./g;
$line =~ s/[\s\.]Geo\s+\./Geo./g;
$line =~ s/[\s\.]Genl\s+\./Genl./g;
$line =~ s/[\s\.]Gen\s+\./Gen./g;
$line =~ s/[\s\.]Gaz\s+\./Gaz./g;
$line =~ s/[\s\.]Fin\s+\./Fin./g;
$line =~ s/[\s\.]Fed\s+\./Fed./g;
$line =~ s/[\s\.]Feb\s+\./Feb./g;
$line =~ s/[\s\.]Fam\s+\./Fam./g;
$line =~ s/[\s\.]Fac\s+\./Fac./g;
$line =~ s/[\s\.]Europ\s+\./Europ./g;
$line =~ s/[\s\.]Eur\s+\./Eur./g;
$line =~ s/[\s\.]Esq\s+\./Esq./g;
$line =~ s/[\s\.]Enr\s+\./Enr./g;
$line =~ s/[\s\.]Eng\s+\./Eng./g;
$line =~ s/[\s\.]Eliz\s+\./Eliz./g;
$line =~ s/[\s\.]Edw\s+\./Edw./g;
$line =~ s/[\s\.]Educ\s+\./Educ./g;
$line =~ s/[\s\.]Dr\s+\./Dr./g;
$line =~ s/[\s\.]Doc\s+\./Doc./g;
$line =~ s/[\s\.]Dist\s+\./Dist./g;
$line =~ s/[\s\.]Dept\s+\./Dept./g;
$line =~ s/[\s\.]Dears\s+\./Dears./g;
$line =~ s/[\s\.]Dal\s+\./Dal./g;
$line =~ s/[\s\.]Ct\s+\./Ct./g;
$line =~ s/[\s\.]Cst\s+\./Cst./g;
$line =~ s/[\s\.]Crim\s+\./Crim./g;
$line =~ s/[\s\.]Cr\s+\./Cr./g;
$line =~ s/[\s\.]Cowp\s+\./Cowp./g;
$line =~ s/[\s\.]Corp\s+\./Corp./g;
$line =~ s/[\s\.]Conv\s+\./Conv./g;
$line =~ s/[\s\.]Cons\s+\./Cons./g;
$line =~ s/[\s\.]Conn\s+\./Conn./g;
$line =~ s/[\s\.]Comp\s+\./Comp./g;
$line =~ s/[\s\.]Comm\s+\./Comm./g;
$line =~ s/[\s\.]Com\s+\./Com./g;
$line =~ s/[\s\.]Colum\s+\./Colum./g;
$line =~ s/[\s\.]Co\s+\./Co./g;
$line =~ s/[\s\.]Cl\s+\./Cl./g;
$line =~ s/[\s\.]Civ\s+\./Civ./g;
$line =~ s/[\s\.]Cir\s+\./Cir./g;
$line =~ s/[\s\.]Chas\s+\./Chas./g;
$line =~ s/[\s\.]Ch\s+\./Ch./g;
$line =~ s/[\s\.]Cf\s+\./Cf./g;
$line =~ s/[\s\.]Cdn\s+\./Cdn./g;
$line =~ s/[\s\.]Cass\s+\./Cass./g;
$line =~ s/[\s\.]Cas\s+\./Cas./g;
$line =~ s/[\s\.]Car\s+\./Car./g;
$line =~ s/[\s\.]Can\s+\./Can./g;
$line =~ s/[\s\.]Calif\s+\./Calif./g;
$line =~ s/[\s\.]Cal\s+\./Cal./g;
$line =~ s/[\s\.]Bros\s+\./Bros./g;
$line =~ s/[\s\.]Bl\s+\./Bl./g;
$line =~ s/[\s\.]Bd\s+\./Bd./g;
$line =~ s/[\s\.]Aust\s+\./Aust./g;
$line =~ s/[\s\.]Aug\s+\./Aug./g;
$line =~ s/[\s\.]Assur\s+\./Assur./g;
$line =~ s/[\s\.]Assn\s+\./Assn./g;
$line =~ s/[\s\.]App\s+\./App./g;
$line =~ s/[\s\.]Am\s+\./Am./g;
$line =~ s/[\s\.]Alta\s+\./Alta./g;
$line =~ s/[\s\.]Admin\s+\./Admin./g;
$line =~ s/[\s\.]Adjut\s+\./Adjut./g;
$line =~ s/[\s\.]APPLIC\s+\./APPLIC./g;

    $$pLine = $line;
}


1;
