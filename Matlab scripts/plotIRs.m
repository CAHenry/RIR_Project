
clear, close all

fs = 44100;
xlims = [10 1000];
flims = [20 20000];
% ylims = [-30 10];
IRlen = 1500; % keep only these many milliseconds of the IRs
IRlen = round(IRlen/1000*fs); % IRlen in samples

%% File names
rootdir = 'Diracs/3DTI recordings 19 august/Dirac1 nodirect/';
filenames = getDirList(rootdir);

refIR_lib_path = 'Diracs/Reference/Recorded_1dirac_Library_nodirect.wav';
refIR_trap_path = 'Diracs/Reference/Recorded_1dirac_Trapezoid_nodirect.wav';

%% Read IRs
nfiles = length(filenames);
IRcell = cell(nfiles,1); % impulse responses
room = zeros(nfiles,1); % room type
refs = zeros(2,1); % reference for the trapezoid and the library (4OA)
for ind=1:nfiles
    % Read IR
    filepath = [rootdir,filenames{ind}];
    [IRcell{ind},fs] = audioread(filepath);
    % Assign room
    if contains(filenames{ind},'Lib')
        room(ind) = 1;
        if contains(filenames{ind},'4OA')
            refs(1) = ind;
        end
    else
        room(ind) = 2;
        if contains(filenames{ind},'4OA')
            refs(2) = ind;
        end
    end
end

%% Throw the reference IRs in there as well
refIR_lib = audioread(refIR_lib_path);
refIR_trap = audioread(refIR_trap_path);
padding = 0.2*fs; % add 200ms of silence to allign it with other IRs
zeropad = zeros(padding,2);
refIR_lib = [zeropad;refIR_lib];
refIR_trap = [zeropad;refIR_trap];
IRcell{end+1} = refIR_lib;
filenames{end+1} = 'Library reference';
room(end+1) = 1;
IRcell{end+1} = refIR_trap;
filenames{end+1} = 'Trapezoid reference';
room(end+1) = 2;
nfiles = nfiles + 2;

%% Allign and window IRs
% We'll find the onset as the maximum of a 3khz-lowpassed IR,
% https://asa.scitation.org/doi/pdf/10.1121/1.4875714?class=pdf
% We'll apply a Hann window
fc = 3000 / (fs / 2); % cutoff frequency (3khz)
[b,a] = butter(10, fc, 'low'); % 10th order Butterworth
slopelen = 128; % hann window slope length in samples
safety = 5; % safety window before the onset (5ms)
IRvec = zeros(IRlen,2,nfiles); % matrix to hold all the IRs
for ind=1:nfiles
    IR = IRcell{ind}; % get IR
    
    % Option 1: find the max using a low-passed version of the IR
    fIR = filter(b,a,IR); % apply low pass
    [~,max_i] = max(fIR(:,1)); % find maximum value of the left channel
    
    % Option 2: just find the max of the IR
%     [~,max_i] = max(IR(:,1)); % find maximum value of the left channel

    % Option 3: just start from t=200ms
    max_i = 0.2*fs;
    
    ind1 = max(1,max_i - round(safety/1000*fs)); % start at the onset - the safety
    ind2 = ind1 + IRlen-1; % end after IRlen ms
    IR = IR(ind1:ind2,:);
    win=hann(slopelen*2-1);
    win=[win(1:slopelen);
         ones(size(IR,1)-2*slopelen,1);
         win(slopelen:end)];
    win = repmat(win,1,size(IR,2));
    IRvec(:,:,ind) = IR.*win;
end

%% Normalize IRs
% We normalize the rms of all IRs to the correspoding reference (4OA IRs).
% Actually most of the IRs are already normalized within +/-1dB, except the
% recorded BRIRs
% for ind=1:nfiles
%     IR = IRvec(:,:,ind); % get IR
%     curr_room = room(ind);
%     ref = IRvec(:,:,refs(curr_room)); % take the reference for this room
%     ref_rms = mean(rms(ref)); % mean rms of left and right channels (ref)
%     curr_rms = mean(rms(IR)); % mean rms of left and right channels (curr) 
%     norm_factor = ref_rms/curr_rms;
%     IRvec(:,:,ind) = IR*norm_factor; % normalize
% end

%% Plot
tvec = 1000*(0:IRlen-1)'/fs;
xlims = [0 200];
Noct = 6;
FRvec = fft(IRvec);
fvec = (0:size(FRvec,1)-1)*fs/size(FRvec,1);
FRsvec = zeros(size(FRvec));
for ind=1:nfiles
    % Plot
    figure
    subplot(2,1,1)
    plot([tvec,tvec],IRvec(:,:,ind))
    xlim(xlims)%, ylim([-irmaxpeak irmaxpeak])
    xlabel('t [ms]'), ylabel('Amplitude'), grid on
    title(sprintf('%s: Kemar BRIR (Az=0,El=0)',filenames{ind}))   
    subplot(2,1,2)
    FR = FRvec(:,:,ind);
    %     FRs = iosr.dsp.smoothSpectrum(abs(FR(:,1)),fvec',Noct); % "proper" smoothing, but terribly slow. Must be done for each channel separately
    FRs = movAvgSmooth(abs(FR),fs,1/Noct); % decent smoothing, fast
    FRsvec(:,:,ind) = FRs;
    semilogx(fvec,db(FRs)), grid on
    title(['Frequency response smoothed 1/',num2str(Noct),' octave']) 
    xlim([fvec(1) fs/2])%, ylim(ylims)
    xlabel('f [Hz]'), ylabel('Magnitude [dB]')
    legend({'Left','Right'},'location','northwest')
end

%% Plot all frequency responses
for r=[1,2]
    ind = room==r & (contains(filenames,'1OA') | contains(filenames,'ref') | contains(filenames,'RVL'))';
    if r==1
        roomname = 'Library';
    else
        roomname = 'Trapezoid';
    end
    figure
%     subplot(1,2,1)
    semilogx(fvec,db(squeeze(FRsvec(:,1,ind)))), grid on
    legend(filenames{ind})
    xlabel('f [Hz]'), ylabel('Magnitude [dB]')
    xlim(flims)
    title([roomname,': Frequency response (1/',num2str(Noct),' octave-smoothed), left channel']) 
%     subplot(1,2,2)
%     semilogx(fvec,db(squeeze(FRsvec(:,2,ind)))), grid on
    xlabel('f [Hz]'), ylabel('Magnitude [dB]')
    xlim(flims)
    title([roomname,': Frequency response (1/',num2str(Noct),' octave-smoothed), right channel']) 
end





% TODO: Clarity/DRR/RT60? Perceived loudness?