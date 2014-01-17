use strict;
use warnings;

#input is the URL to the TREC overview page of the results for a particular task

my $numArgs=$#ARGV+1;
if($numArgs<2)
{
    print "Usage: [URL to TREC overview page] [output directory] [filter: term that needs to occur valid input files]\n";
    exit;
}

my $filter="";

if($numArgs==3)
{
    $filter=$ARGV[2];
    print "Filter set to $filter, ignoring all files on a path lacking this term\n";
}

#LOGIN/PASSWORD for the TREC data site!
my $user = "";
my $pw = "";


my $url = $ARGV[0];

`curl -u $user:$pw $url > tmp1`;
print "Downloaded tmp1\n";

my $index = rindex($url,'/');
$url = substr($url,0,$index+1);

print "Extracted url: $url\n";

my @files = ();
open(IN,"tmp1")||die $!;
while(<IN>)
{
    #<LI><A HREF="adhoc/input.8manexT3D1N0.gz"> input.8manexT3D1N0.gz </A>
    chomp;
    if($_=~m/<LI><A HREF/i )
    {
  my $file = $_;
  $file=~s/.*HREF="//i;
  $file=~s/".*//;

  my $path = $url.$file;
  print "Found $path\n";

  if(length($filter)>0)
  {
      if($path=~m/$filter/){;}
      else{next;}
  }
  push(@files,$path);
    }
}
close(IN);

my $outputDir = $ARGV[1];
if($outputDir=~m/\/$/){;}
else{$outputDir=$outputDir."/";}
print "Creating $outputDir\n";
`mkdir $outputDir`;
print "Attempting to download files ... \n";
foreach my $file(@files)
{
  my $name = $file;
  $name=~s/.*\///;

  my $outputPath = $outputDir.$name;
  print "Downloading $file to $outputPath\n";

  `curl -u $user:$pw $file > $outputPath`;
}
