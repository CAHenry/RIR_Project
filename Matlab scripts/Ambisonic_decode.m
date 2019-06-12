% requires polarch-Higher-Order-Ambisonics-39eea5a

indir = 'ambisonic_minus12db/';
outdir = 'ambisonic_decoded/';
rooms = {'Library','Trapezoid'};
azimuths = [0, 30, 330];

for indroom = 1:length(rooms)
    
    room = rooms{indroom};
    if ~exist([outdir,room], 'dir')
        mkdir([outdir,room])
    end
    
    for indaz = 1:length(azimuths)
        
        azimuth = azimuths(indaz);
        
        infile = [room,'_Eigenmike_',num2str(azimuth),'_Ambi4OA.wav'];
        hoasig4thorder = audioread([indir,infile]);

        for order=0:1:4
            
            if ~exist([outdir,room,'/',num2str(order),'OA'], 'dir')
                mkdir([outdir,room,'/',num2str(order),'OA'])
            end

            nambichannels = (order+1)^2;
            hoasig = hoasig4thorder(:,1:nambichannels);

            outfile = [room,'_',num2str(order),'OA_',num2str(azimuth),'_Impulse.wav'];

            if order == 1 || order == 0 % we will use 6 loudspeakers for the 0th order (ideally it would be diotic but the toolkit doesn't allow that) 
                ls_dirs_rad = [0      0
                               pi/2   0
                               pi     0
                               3*pi/2 0
                               0      pi/2
                               0     -pi/2];
            elseif order == 2
                [~, ls_dirs_rad] = platonicSolid('icosahedron');
            elseif order == 3
                [~, ls_dirs_rad] = platonicSolid('dodecahedron');
            elseif order == 4
                [az,el] = pentakis_dodecahedron();
                ls_dirs_rad = [az,el];
            end

            ls_dirs = ls_dirs_rad*180/pi;

            %ls_num = size(ls_dirs,1);
            % get order
        %     N = floor(sqrt(ls_num) - 1);
            % get a projection (sampling) decoder
            D_sad = ambiDecoder(ls_dirs, 'sad', 0, order);%N);
            % decode signals
            lssig = decodeHOA_N3D(hoasig, D_sad);

            audiowrite([outdir,room,'/',num2str(order),'OA/',outfile], lssig, 44100)

        end
    end
end