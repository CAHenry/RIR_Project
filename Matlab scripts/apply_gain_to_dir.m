
% Apply some gain to all wav files in a folder

indir = 'ambisonic';
outdir = 'ambisonic_minus12db';

gain_db = -12;
gain = 10.^(gain_db/20);

if exist(outdir,'dir')
    %error(sprintf('Directory %s already exists',outdir))
else
    mkdir(outdir);
end

filelist = getDirList(indir);
nfiles = length(filelist);
for ind=1:length(filelist)
    infile = filelist{ind};
    [x,fs] = audioread([indir,'/',infile]);
    y = x.*gain;
    audiowrite([outdir,'/',infile],y,fs,'BitsPerSample',24);
end
