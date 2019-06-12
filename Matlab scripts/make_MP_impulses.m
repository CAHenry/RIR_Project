
% Make mono panned impulses (just take the W channel)

indir = 'ambisonic/';
outdir = 'MP/';

rooms = {'Library','Trapezoid'};
azimuths = [0, 30, 330];

for indroom = 1:length(rooms)
    
    room = rooms{indroom};
    if ~exist([outdir,room], 'dir')
        mkdir([outdir,room])
    end
    
    if ~exist([outdir,room,'/MP'], 'dir')
        mkdir([outdir,room,'/MP'])
    end
    
    for indaz = 1:length(azimuths)
 
        azimuth = azimuths(indaz);
        
        infile = [room,'_Eigenmike_',num2str(azimuth),'_Ambi4OA.wav'];
        outfile = [room,'_MP_',num2str(azimuth),'_Impulse.wav'];
        x = audioread([indir,infile]);
        y = x(:,1); % W channel
        audiowrite([outdir,room,'/MP/',outfile], y, 44100)

    end
end