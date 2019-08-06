% requires polarch-Higher-Order-Ambisonics-39eea5a

% We are trying to replicate Fig.4 from Gavin Kearney's paper about
% distance perception vs Ambisonic order. The idea is to decode an
% ambisonic RIR into a configuration of many (180) loudspeakers in the
% horizontal plane and then plot each loudspeaker feed's gain as a point
% using imagesc, where the x coordinate is the azimuth and the y coordinate
% is time.

indir = 'RVL_ambisonic_withdirect/';
% outdir = 'ambisonic_decoded_horzplane/';
rooms = {'Trapezoid'};
% azimuths = {'0','90','270'};
azimuths = {'180_reversed','90_reversed','270_reversed'};

tstart = 1;%0.1*44100; % IR starts at t=0.1s % NOTE: only use for the impulses with the direct sound

len = round(0.03*44100); % keep only the first 30ms
tvec = (0:len-1)/44100;

c = 343; % speed of sound (m/s)

fc = 20000 / (44100 / 2); % cutoff frequency (3khz)
[b,a] = butter(10, fc, 'low'); % 10th order Butterworth

for indroom = 1:length(rooms)
    
    room = rooms{indroom};
    
    for indaz = 1:length(azimuths)
        
        azimuth = azimuths{indaz};
        
        infile = [room,'_RVL_',azimuth,'_Ambi4OA.wav'];
        [hoasig4thorder,fs] = audioread([indir,infile]);
        hoasig4thorder = hoasig4thorder(tstart:tstart+len-1,:);
        
        if contains(azimuth,'reversed')
            % ROTATE 180 degrees around Z axis because we had the eigenmike
            % facing the other way around
            disp("Rotating 180 degrees around Z axis...")
            hoasig4thorder = rotateHOA_N3D(hoasig4thorder,180,0,0);
            azimuth = azimuth(1:strfind(azimuth,'_')-1);
        end
        
        hoasig4thorder = filter(b,a,hoasig4thorder);

        for order=4:1:4
           
            %% Gavin Kearney's method - decoding to horizontal ring of ls

            nambichannels = (order+1)^2;
            hoasig = hoasig4thorder(:,1:nambichannels);
            ls_dirs = linspace(-180,180,180)';
            ls_dirs = [ls_dirs,zeros(size(ls_dirs))];
            D_sad = ambiDecoder(ls_dirs, 'sad', 0, order);
            
            % decode signals
            lssig = decodeHOA_N3D(hoasig, D_sad);
            
            %plot
% %             lssig = lssig./max(max(abs(lssig)));
%             dbsig = db(lssig);
%             dbsig(dbsig<-60) = -60;
%             figure, s = surf(ls_dirs(:,1),tvec,dbsig);
% %             colormap(flipud(gray))
%             view(2) % vertical view
%             s.EdgeColor = 'none'; % remove surface lines
%             set(gca,'YDir','reverse')
% %             caxis([-1 1])
% %             zlim([-1 1])
%             title(sprintf('room=%s, azimuth=%d, order=%d',room,azimuth,order))
%             caxis([-30 0])
%             zlim([-60 0])
%             xlabel('Azimuth [degrees]')
%             ylabel('t [s]')

            %% Get pressure at the center point according to eq 6.13 from [1]

            nfft = 2^nextpow2(size(hoasig,1));
            fvec = (0:nfft-1)'*fs/nfft;
            b_W = fft(hoasig,nfft);
            b_W = b_W(1:end/2+1,:); % keep only up to Nyquist frequency
         
            N = order;
            
            dir_ev = [linspace(-180,180,180)',zeros(180,1)]; % direction to be evaluated
            Y_ev = getRSH(N,dir_ev); % encode in the SH domain

            j_vec=1; % uncomment if not using the Bessel function below
            
            % Bessel function -> KEEP COMMENTED because it doesn't seem to
            % work: it produces weird-looking IRs
%             r = 1; % distance
%             j_vec = zeros(size(b_W)); % bessel function
%             for row = 1:size(b_W,1)
%                 f = fvec(row); % frequency (indicated by the row)
%                 k = 2*pi*f/c; % wave number
%                 for col = 1:size(b_W,2)
%                     n = floor(sqrt(col-1)); % Ambisonic order (indicated by column)
%                     j_vec(row,col) = sqrt(pi/(2*k*r))*besselj(n+0.5,k*r);
%                     j_vec(row,col) = j_vec(row,col)*exp(-1i*k*r); % propagation delay?
%                 end
%             end     
%             j_vec(1,:) = j_vec(2,:); % f=0 is all NaNs. Replace it with the next value
            
            p = b_W.*j_vec*Y_ev;
            
            p = [p; flipud(conj(p(2:end-1,:)))]; % reconstruct full spectrum
            p(1,:) = real(p(1,:));
            p(end/2+1,:) = real(p(end/2+1,:));
            
            dbp = db(abs(p));
            dbp(dbp<-60) = -60;

%             figure, s = surf(dir_ev(:,1),fvec,dbp);
%             view(2) % vertical view
%             s.EdgeColor = 'none'; % remove surface lines
%             set(gca,'YDir','reverse')
%             set(gca,'yscale','log') % log scale for frequency axis
%             xlabel('Azimuth (deg)')
%             ylabel('Frequency (Hz)')
%             ylim([200,fs/2])
%             caxis([-30 0])
%             %zlim([-60 0])
            
            % Now in the time domain 
            p_t = ifft(p);
            p_t = p_t(1:len,:); % keep the first 'len' samples
            fprintf('Normalizing by %0.2f\n',max(max(abs(p_t))));
            p_t = p_t./max(max(abs(p_t)));
            dbsig = db(p_t);
            dbsig(dbsig<-60) = -60;
            figure, s = surf(dir_ev(:,1),tvec,dbsig);
            colormap(flipud(gray))
            view(2) % vertical view
            s.EdgeColor = 'none'; % remove surface lines
            set(gca,'YDir','reverse')
            set(gca,'XDir','reverse')
%             caxis([-1 1])
%             zlim([-1 1])
            title(sprintf('SH room=%s, azimuth=%s, order=%d',room,azimuth,order))
            caxis([-50 0])
            zlim([-60 0])
            xlabel('Azimuth [degrees]')
            ylabel('t [s]')
        end
    end
end