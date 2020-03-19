%% Directional plot ambisonics
% requires polarch-Higher-Order-Ambisonics-39eea5a

% We are trying to replicate Fig.4 from Gavin Kearney's paper about
% distance perception vs Ambisonic order. The idea is to decode an
% ambisonic RIR into a configuration of many (180) loudspeakers in the
% horizontal plane and then plot each loudspeaker feed's gain as a point
% using imagesc, where the x coordinate is the azimuth and the y coordinate
% is time.

% TODO: plotHOA, show precedence effect time window

clear, close all

figdir = 'figures';
if ~isfolder(figdir)
    mkdir(figdir);
end
if ~isfolder(fullfile(figdir,'png'))
    mkdir(fullfile(figdir,'png'))
end

indir = 'ambisonic_withdirect_denoised/';
rooms = {'Trapezoid','Library'};
azimuths = [0,30,330];

len = round(0.5*44100); % keep only the first 30ms, EDIT: 500ms
tvec = (0:len-1)/44100;

fc = 20000 / (44100 / 2); % cutoff frequency (3khz)
[b,a] = butter(10, fc, 'low'); % 10th order Butterworth

for indroom = 1:length(rooms)
    
    room = rooms{indroom};
    
    for indaz = 1:length(azimuths)
        
        azimuth = azimuths(indaz);
        
        infile = [room,'_Eigenmike_',num2str(azimuth),'_Ambi4OA.wav'];
        [hoasig4thorder,fs] = audioread([indir,infile]);
        hoasig4thorder = filter(b,a,hoasig4thorder);
        
        % Allign and window IRs
        safety = 0.1; % safety window before the onset (0.1ms)
        [~,max_i] = max(abs(hoasig4thorder)); % get the onset for each HOA channel as the peak value
        max_i = min(max_i); % select the earliest onset
        ind1 = max_i - round(safety/1000*fs); % start at the onset - the safety interval
        ind2 = ind1 + len-1; % end after len ms
        hoasig4thorder = hoasig4thorder(ind1:ind2,:);

        orders = 0:1:4;
        norders = numel(orders);
        f = figure('pos',[37.8000 205.8000 1.4136e+03 318.4000]);
        count = 1;
        for order=orders
            ax(count) = subplot(1,norders,count);
            nambichannels = (order+1)^2;
            hoasig = hoasig4thorder(:,1:nambichannels);
            plotHOA(hoasig,false)
            title(sprintf('SH order=%d',order))
            
%             plotHOA2(hoasig)
%             title(sprintf('EDD room=%s, azimuth=%d, order=%d',room,azimuth,order))
            count = count+1;
        end
        sgtitle(sprintf('SH plot room=%s, azimuth=%d',room,azimuth))
        figname = sprintf('SH plot %s %d',room,azimuth);
        saveas(f,[figdir,'/png/',figname,'.png'])
        for count = 1:numel(ax)
            pos = get(ax(count),'Position');
            set(ax(count),'View',[-45 45])
            set(ax(count),'Position',pos);
        end
        figname = sprintf('SH plot %s %d tilted',room,azimuth);
        saveas(f,[figdir,'/png/',figname,'.png'])
    end
end