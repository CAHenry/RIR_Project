
% Plot IACC data from BRIRs

clear%, close all

figdir = 'figures';
if ~isfolder(figdir)
    mkdir(figdir);
end
if ~isfolder(fullfile(figdir,'png'))
    mkdir(fullfile(figdir,'png'))
end

rootdir = '3DTI recordings 9 nov';
names = {'0OA','1OA','2OA','3OA','4OA','RVL','Recorded'};
rt = [1.5 0.9]; % cutoff times for either room (larger than t60 in any case)
roomnames = {'Library','Trapezoid'};
nfiles = numel(names);
nrooms = numel(roomnames);
filenames = cell(nfiles,nrooms);
for i=1:nfiles
    for j=1:nrooms
        filenames{i,j} = sprintf('%s_%s_Dirac.wav',roomnames{j},names{i});
    end
end

%% Frequency ranges to evaluate IACC
oct500 = round(500 * [2^(-0.5), 2^(0.5)]);
oct1000 = round(1000 * [2^(-0.5), 2^(0.5)]);
oct2000 = round(2000 * [2^(-0.5), 2^(0.5)]);

%% Read files and get IACC
data = cell(nfiles,nrooms);
iacc = cell(nfiles,nrooms);
iacc500 = struct('early',zeros(nfiles,nrooms),'late',zeros(nfiles,nrooms));
iacc1000 = struct('early',zeros(nfiles,nrooms),'late',zeros(nfiles,nrooms));
iacc2000 = struct('early',zeros(nfiles,nrooms),'late',zeros(nfiles,nrooms));
bqi = struct('early',zeros(nfiles,nrooms),'late',zeros(nfiles,nrooms));
for i=1:nfiles
    for j=1:nrooms
        % Read file
        filepath = fullfile(rootdir,filenames{i,j});
        [y,fs] = audioread(filepath);
        % Trim before onset
        ons = int32(min(AKonsetDetect(y))) - 64; % add some safety samples
        y = y(ons:end,:);
        % Trim after RT
        rt_samples = round(rt(j)*fs);
        if mod(rt_samples,2) % if odd, add 1
            rt_samples = rt_samples + 1;
        end
        yt = y(1:rt_samples,:);
%         figure
%         subplot(2,1,1), plot((1:size(y,1))/fs,db(y)), title(names{i})
%         subplot(2,1,2), plot((1:size(yt,1))/fs,db(yt))
        y = yt;
        % Window
        fadelen = 32;
        winhan = hann(2*fadelen-1);
        winhan = repmat(winhan(fadelen:end),1,size(y,2));
        y(end-fadelen+1:end,:) = y(end-fadelen+1:end,:).*winhan;
        % Denoise (only for recorded BRIRs)
%         if strcmp(names{i},'Recorded')
%             ydn = denoise_RIR(y,fs,4000,125,1);
%         end
        % Create ITA object
        data{i,j} = itaAudio(y,fs,'time');
        data{i,j}.channelNames = {'Left';'Right'};
        % Get IACC
        iacc{i,j} = ita_roomacoustics_IACC(data{i,j});
        ind500 = iacc{i,j}.IACC_early.freqVector>=oct500(1)&iacc{i,j}.IACC_early.freqVector<=oct500(2);
        ind1000 = iacc{i,j}.IACC_early.freqVector>=oct1000(1)&iacc{i,j}.IACC_early.freqVector<=oct1000(2);
        ind2000 = iacc{i,j}.IACC_early.freqVector>=oct2000(1)&iacc{i,j}.IACC_early.freqVector<=oct2000(2);
        iacc500.early(i,j) = mean(iacc{i,j}.IACC_early.freq(ind500));
        iacc500.late(i,j) = mean(iacc{i,j}.IACC_late.freq(ind500));
        iacc1000.early(i,j) = mean(iacc{i,j}.IACC_early.freq(ind1000));
        iacc1000.late(i,j) = mean(iacc{i,j}.IACC_late.freq(ind1000));
        iacc2000.early(i,j) = mean(iacc{i,j}.IACC_early.freq(ind2000));
        iacc2000.late(i,j) = mean(iacc{i,j}.IACC_late.freq(ind2000));
        bqi.early(i,j) = 1 - (iacc500.early(i,j) + iacc1000.early(i,j) + iacc2000.early(i,j))/3;
        bqi.late(i,j) = 1 - (iacc500.late(i,j) + iacc1000.late(i,j) + iacc2000.late(i,j))/3;
    end
end

%% Plot BRIRs in time and frequency domain
for j=1:nrooms
    f = figure('pos',[37.8000 205.8000 1.4136e+03 318.4000]);
    count = 1;
    for i=1:nfiles
        ax(i) = subplot(2,nfiles,i);
        AKp(data{i,j}.time,'et2d','fs',fs)
        title(names{i})
        ax(i+nfiles) = subplot(2,nfiles,i+nfiles);
        AKp(data{i,j}.time,'m2d','fs',fs,'frac',3)
        title('')
    end
    sgtitle(sprintf('BRIRs %s',roomnames{j}))
end

%% Plot early and late IACC
c = parula(nfiles+1);
for j=1:nrooms
    f = figure('pos',[188.2000 85 1.1488e+03 684.8000]);
    ax1 = subplot(2,1,1); hold(ax1,'on')
    ax2 = subplot(2,1,2); hold(ax2,'on')
    for i=1:nfiles
        iacc{i,j}.IACC_early.plot_freq('figure_handle',f,'axes_handle',ax1,'hold','on','color',c(i,:));
        iacc{i,j}.IACC_late.plot_freq('figure_handle',f,'axes_handle',ax2,'hold','on','color',c(i,:));
    end
    title(ax1,sprintf('%s early (<80ms) IACC',roomnames{j}))
    title(ax2,sprintf('%s late (>80ms) IACC',roomnames{j}))
    legend(names,'interpreter','none','location','best')
    figname = sprintf('IACC %s',roomnames{j});
    saveas(f,[figdir,'/png/',figname,'.png'])
end

%% Plot single value IACC in the 3 relevant bands
% c = parula(nfiles+1);
% for j=1:nrooms
%     f = figure('pos',[10.6000 65 1.0448e+03 618.4000]);
%     ax1 = subplot(2,1,1); hold(ax1,'on')
%     ax2 = subplot(2,1,2); hold(ax2,'on')
%     xl = {'IACC500','IACC1000','IACC2000'};
%     for i=1:nfiles
%         plot(ax1,[iacc500.early(i,j),iacc1000.early(i,j),iacc2000.early(i,j)],'-x','color',c(i,:));
%         plot(ax2,[iacc500.late(i,j),iacc1000.late(i,j),iacc2000.late(i,j)],'-x','color',c(i,:));
%     end
%     grid(ax1,'on'); xticks(ax1,1:3), xticklabels(ax1,xl), ylim(ax1,[0 1.05]), ylabel('IACC')
%     grid(ax2,'on'); xticks(ax2,1:3), xticklabels(ax2,xl), ylim(ax2,[0 1.05]), ylabel('IACC')
%     title(ax1,sprintf('%s early IACC',roomnames{j}))
%     title(ax2,sprintf('%s late IACC',roomnames{j}))
%     legend(names,'interpreter','none','location','best')
% end

%% Plot early and late BQI
c = parula(nfiles+1);
for j=1:nrooms
    f = figure('pos',[10.6000 65 1.0448e+03 618.4000]);
    ax1 = subplot(2,1,1); hold(ax1,'on')
    ax2 = subplot(2,1,2); hold(ax2,'on')
    plot(ax1,1:nfiles,bqi.early(:,j),'-x')
    plot(ax2,1:nfiles,bqi.late(:,j),'-x')
    grid(ax1,'on'); xticks(ax1,1:nfiles), xticklabels(ax1,names), ylim(ax1,[0 1.05]), ylabel(ax1,'BQI')
    grid(ax2,'on'); xticks(ax2,1:nfiles), xticklabels(ax2,names), ylim(ax2,[0 1.05]), ylabel(ax2,'BQI')
    title(ax1,sprintf('%s early (<80ms) BQI',roomnames{j}))
    title(ax2,sprintf('%s late (>80ms) BQI',roomnames{j}))
    figname = sprintf('BQI %s',roomnames{j});
    saveas(f,[figdir,'/png/',figname,'.png'])
end
