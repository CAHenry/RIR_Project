
% TODO: direct TakeFive Trapezoid is missing. It should be easy to record
% again; a better way to calculate P is to divide the rms of the direct
% over the direct+reverb (the actual recording); save variables in a file
% and give the option to load them because it takes forever; also plot
% progress for the same reason

% Plot RAP model data from recordings

clear, close all

figdir = 'figures';
if ~isfolder(figdir)
    mkdir(figdir);
end
if ~isfolder(fullfile(figdir,'png'))
    mkdir(fullfile(figdir,'png'))
end

do_analysis = false;
% freqspace = logspace(log10(125),log10(16000),8); % 125 to 16000 Hz (7 oct) % EDIT: using whatever IACC is spitting out
framelength = 1; % 100 ms frames
thresh = -10; % db less than the integrated loudness value (change it to something less arbitrary if needed)

excludeDirect = true;
normalize = true;
rootdir = '3DTI recordings 9 nov';
names = {'Direct','0OA','1OA','2OA','3OA','4OA','RVL'};
roomnames = {'Library','Trapezoid'};
prognames = {'Speech','TakeFive'};
nfiles = numel(names);
nrooms = numel(roomnames);
nprogs = numel(prognames);
filenames = cell(nfiles,nrooms,nprogs);
for i=1:nfiles
    for j=1:nrooms
        for k=1:nprogs
            filenames{i,j,k} = sprintf('%s_%s_%s.wav',roomnames{j},names{i},prognames{k});
        end
    end
end

%% Read files and get IACC
if do_analysis
    data = cell(nfiles,nrooms,nprogs);
    ASW = zeros(nfiles,nrooms,nprogs);
    LEV = zeros(nfiles,nrooms,nprogs);
    P_all = cell(nfiles,nrooms,nprogs);
    iacc_all = cell(nfiles,nrooms,nprogs);
    for i=1:nfiles
        fprintf('Analyzing file %d/%d (%s)...\n',i,nfiles,names{i});
        for j=1:nrooms
            fprintf('Analyzing room %d/%d (%s)...\n',j,nrooms,roomnames{j});
            for k=1:nprogs
                fprintf('Analyzing program %d/%d (%s)',k,nprogs,prognames{k});
                % Read file
                filepath = fullfile(rootdir,filenames{i,j,k});
                [y,fs] = audioread(filepath);
                len = round(framelength*fs);
                N = floor(size(y,1)/len); % number of time frames
                C = 31; % numel(freqspace)-1; % number of freq channels
                iacc = zeros(N,C);
                P = zeros(N,C);
                for n = 1:N
                    fprintf('.');
                    ind1 = 1+(n-1)*len;
                    ind2 = min(ind1+len-1,size(y,1));
                    buf = y(ind1:ind2,:);
                    % Create ITA object
                    d = itaAudio(buf,fs,'time');
                    d.channelNames = {'Left';'Right'};
                    % Get IACC
                    iaccFull = ita_roomacoustics_IACC(d); % 1/3 octave bands
                    iacc(n,:) = iaccFull.IACC_fullTime.freq;
                    % Get probability of direct sound
                    % Read direct-only recording
                    filepath_d = fullfile(rootdir,sprintf('%s_Direct_%s.wav',roomnames{j},prognames{k}));
                    [y_d,fs] = audioread(filepath_d);
                    buf_d = y_d(ind1:ind2,:);
                    buf_d_avg = mean(buf_d,2);
                    buf_avg = mean(buf,2);
                    d_avg = itaAudio(buf_avg,fs,'time');
                    d_d_avg = itaAudio(buf_d_avg,fs,'time');
                    d_frac = ita_fractional_octavebands(d_avg, 'bandsPerOctave', 3, 'freqrange', [20 20000], 'zerophase');
                    d_d_frac = ita_fractional_octavebands(d_d_avg, 'bandsPerOctave', 3, 'freqrange', [20 20000], 'zerophase');
                    P(n,:) = rms(d_d_frac.time)./rms(d_frac.time);
                end
                P(P>1) = 1; % limit P to 1 (numerical errors)
                % Calculate ASW and LEV according to the paper
                ASW(i,j,k) = 1 - sum(sum(iacc.^4.*P,'omitnan'))/sum(P(:),'omitnan');
                LEV(i,j,k) = 1 - sum(sum(iacc.^4.*(1-P),'omitnan'))/sum(P(:),'omitnan');
                fprintf('\nASW=%0.4f, LEV=%0.4f\n',ASW(i,j,k),LEV(i,j,k));
                P_all{i,j,k} = P;
                iacc_all{i,j,k} = iacc;
            end
        end
    end

    save('analyzeRecordings_results','data','ASW','LEV','P_all','iacc_all');
end

%% Load
load('analyzeRecordings_results','data','ASW','LEV','P_all','iacc_all');
if excludeDirect
    data = data(2:end,:,:);
    ASW = ASW(2:end,:,:);
    LEV = LEV(2:end,:,:);
    P_all = P_all(2:end,:,:);
    iacc_all = iacc_all(2:end,:,:);
    names = names(2:end);
    nfiles = numel(names);
end
if normalize
   min_asw = min(ASW(:));
   max_asw = max(ASW(:));
   ASW = (ASW - min_asw)/(max_asw-min_asw);
   min_lev = min(LEV(:));
   max_lev = max(LEV(:));
   LEV = (LEV - min_lev)/(max_lev-min_lev);
end
iacc_avg = zeros(size(ASW));
for i=1:nfiles
    for j=1:nrooms
        for k=1:nprogs
            iacc_avg(i,j,k) = mean(iacc_all{i,j,k}(:),'omitnan');
        end
    end
end

%% Plot ASW, LEV, IACC
for j=1:nrooms
    f = figure('pos',[188.2000 85 1.1488e+03 684.8000]);
    ax1 = subplot(3,1,1);
    ax2 = subplot(3,1,2);
    ax3 = subplot(3,1,3);
    c = lines;
    m = 'xod';
    for k = 1:nprogs
        plot(ax1,1:nfiles,ASW(:,j,k),'x-','color',c(k,:),'marker',m(k)), hold(ax1,'on')
        plot(ax2,1:nfiles,LEV(:,j,k),'x-','color',c(k,:),'marker',m(k)), hold(ax2,'on')
        plot(ax3,1:nfiles,iacc_avg(:,j,k),'x-','color',c(k,:),'marker',m(k)), hold(ax3,'on')
    end
    title(ax1,sprintf('%s ASW',roomnames{j})), ylabel(ax1,'ASW')
    xticks(ax1,1:nfiles), xticklabels(ax1,names), grid(ax1,'on'), ylim(ax1,[0 1.05])
    legend(ax1,prognames,'location','best')
    title(ax2,sprintf('%s LEV',roomnames{j})), ylabel(ax2,'LEV')
    xticks(ax2,1:nfiles), xticklabels(ax2,names), grid(ax2,'on'), ylim(ax2,[0 1.05])
    legend(ax2,prognames,'location','best')
    title(ax3,sprintf('%s IACC',roomnames{j})), ylabel(ax3,'IACC')
    xticks(ax3,1:nfiles), xticklabels(ax3,names), grid(ax3,'on'), ylim(ax3,[0 1.05])
    legend(ax3,prognames,'location','best')
    
    figname = sprintf('recordings %s',roomnames{j});
    saveas(f,[figdir,'/png/',figname,'.png'])
end

