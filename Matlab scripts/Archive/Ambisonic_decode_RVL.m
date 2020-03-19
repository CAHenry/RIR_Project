% requires polarch-Higher-Order-Ambisonics-39eea5a

indir = 'RVL_ambisonic_minus12db/';
outdir = 'RVL_ambisonic_decoded/';
rooms = {'Library','Trapezoid'};
azimuths = {'0','90','180','270','top','bottom','0_reversed','90_reversed','180_reversed','270_reversed','top_reversed','bottom_reversed'};

for indroom = 1:length(rooms)
    
    room = rooms{indroom};
    if ~exist([outdir,room], 'dir')
        mkdir([outdir,room])
    end
    
    for indaz = 1:length(azimuths)
        
        azimuth = azimuths{indaz};
        
        infile = [room,'_RVL_',azimuth,'_Ambi4OA.wav'];
        if ~exist([indir,infile],'file')
            fprintf('File %s not found, continuing...\n',[indir,infile]);
            continue
        end
        hoasig4thorder = audioread([indir,infile]);
        
        if contains(azimuth,'reversed')
            % ROTATE 180 degrees around Z axis because we had the eigenmike
            % facing the other way around
            disp("Rotating 180 degrees around Z axis...")
            hoasig4thorder = rotateHOA_N3D(hoasig4thorder,180,0,0);
            azimuth = azimuth(1:strfind(azimuth,'_')-1);
        end

        for order=4
            
            if ~exist([outdir,room,'/RVL_',num2str(order),'OA'], 'dir')
                mkdir([outdir,room,'/RVL_',num2str(order),'OA'])
            end

            nambichannels = (order+1)^2;
            hoasig = hoasig4thorder(:,1:nambichannels);

            outfile = [room,'_RVL_',num2str(order),'OA_',azimuth,'_Impulse.wav'];

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

            audiowrite([outdir,room,'/RVL_',num2str(order),'OA/',outfile], lssig, 44100,'BitsPerSample',24)

        end
    end
end