
% Convolve a dry audio file with all the files in a directory

audiofileroot = 'Dry audio/';
audiofile = 'TakeFive_Drums.wav';
indirroot = 'Diracs/3DTI recordings 19 august calibrated/';
indir = 'Dirac1 withdirect/'; % 'CorrectedDRR';

pos = strfind(audiofile,'.wav');
audioname = audiofile(1:pos-1);

outdir = ['Stimuli/',audioname,'_',indir];

if exist(outdir,'dir')
    error(sprintf('Directory %s already exists',outdir))
else
    mkdir(outdir);
end

[dry,fs] = audioread([audiofileroot,audiofile]);

filelist = getDirList([indirroot,indir]);
nfiles = length(filelist);
y_vec = cell(nfiles,1);
max_peak = 0;
for ind=1:length(filelist)
    infile = filelist{ind};
    [x,fs1] = audioread([indirroot,indir,'/',infile]);
    if fs1~=fs
        error('Sampling frequency mismatch')
    end
    y = fftfilt(x,dry);
    peak = max(max(abs(y)));
    if peak > max_peak
        max_peak = peak;
    end
    y_vec{ind} = y;
end

if max_peak > 1
    fprintf('To prevent clipping, all audio files were normalized by %0.2f dB\n',db(max_peak));
    norm = max_peak;
else
    norm = 1;
end

for ind=1:nfiles
    outfile = filelist{ind};
    y_vec{ind} = y_vec{ind}./norm;
    audiowrite([outdir,'/',outfile],y_vec{ind},fs);
end
