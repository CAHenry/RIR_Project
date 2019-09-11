
% In this script, we adjust our RIRs to the reference. This is done in two
% steps:
%
%   1. Direct-to-Reverberant Ratio (DRR) adjustment. Because we are
%   rendering the direct path and reverb separately, we need to adjust the
%   ratio between the two. To do so, we take a reference impulse (Kemar
%   BRIR at 0 degrees) from each room and compare it with one of the
%   RIRs that we will use in the test. We chose the condition 4OA for this,
%   because is the reference condition in the MUSHRA test.
%
%   2. After the DRR is adjusted, we make sure that all conditions are
%   level-normalised. Because the direct path is the same for all, we just
%   normalise the reverberant tail.

fs = 44100;

%% File paths

rootDir = 'Diracs/';
recordingsDir = [rootDir,'3DTI recordings 19 august calibrated/'];

% DRR stuff
refPath_lib = [rootDir,'Reference/Recorded_1dirac_Library.wav'];
refPath_trap = [rootDir,'Reference/Recorded_1dirac_Trapezoid.wav'];
drrPath_lib = [recordingsDir,'Dirac1 withdirect/4OA_Library_withdirect.wav'];
drrPath_trap = [recordingsDir,'Dirac1 withdirect/4OA_Trapezoid_withdirect.wav'];

% Level normalisation stuff
noDirectDir = [recordingsDir,'Dirac1 nodirect/'];

% Dry audio
speechPath = 'Dry audio/Speech.wav';
drumsPath = 'Dry audio/TakeFive_Drums.wav';

%% 1. DRR adjustment

disp('DRR adjustment')
disp('--------------')

% First, we open the reference BRIRs
disp('Calculating DRR for Kemar BRIR (reference)...')
[~,DRR_ref_lib]=iosr.acoustics.irStats(refPath_lib);
[~,DRR_ref_trap]=iosr.acoustics.irStats(refPath_trap);
fprintf('Reference DRR Library: %0.2fdB (left), %0.2fdB (right)\n',DRR_ref_lib);
fprintf('Reference DRR Trapezoid: %0.2fdB (left), %0.2fdB (right)\n',DRR_ref_trap);

% Then, we open the RIRs that we are using in the test. In this case, 4OA.
disp('Calculating DRR for 3DTI-recorded 4OA (MUSHRA reference)...')
[~,DRR_4OA_lib]=iosr.acoustics.irStats(drrPath_lib);
[~,DRR_4OA_trap]=iosr.acoustics.irStats(drrPath_trap);
fprintf('4OA DRR Library: %0.2fdB (left), %0.2fdB (right)\n',DRR_4OA_lib);
fprintf('4OA DRR Trapezoid: %0.2fdB (left), %0.2fdB (right)\n',DRR_4OA_trap);

% Print results
DRR_adj_lib_LR = -(DRR_ref_lib - DRR_4OA_lib);
DRR_adj_trap_LR = -(DRR_ref_trap - DRR_4OA_trap);
DRR_adj_lib = mean(DRR_adj_lib_LR);
DRR_adj_trap = mean(DRR_adj_trap_LR);
fprintf('Library 4OA reverb should be adjusted by %0.2fdB\n',DRR_adj_lib);
fprintf('Trapezoid 4OA reverb should be adjusted by %0.2fdB\n',DRR_adj_trap);

%% 2. Level normalisation

disp('Level normalisation')
disp('-------------------')

filenames = getDirList(noDirectDir);
nfiles = length(filenames);

% Dry audio files
[dry_speech, fs_temp] = audioread(speechPath);
dry_speech = [dry_speech,dry_speech]; % make it stereo
if fs_temp ~= fs
    error('Sampling frequency mismatch!');
end
[dry_drums, fs_temp] = audioread(drumsPath);
dry_drums = [dry_drums,dry_drums]; % make it stereo
if fs_temp ~= fs
    error('Sampling frequency mismatch!');
end

% Table to store the data
columns = {'Condition','Room','IntLoud_Speech','IntLoud_Drums','Correction_DRR','Correction_IntLoudAvg','Correction_Perceptual','Correction_Total','IRData'};
T = table({},{},[],[],[],[],[],[],{},'VariableNames',columns);

% Iterate through all the files in the folder and fill the table
disp('Reading audio files...')
for filename = filenames 
    filename = filename{1};
    % Read audio file
    filepath = [noDirectDir,filename];
    [y,fs_temp] = audioread(filepath);
    if fs_temp ~= fs
        error('Sampling frequency mismatch!');
    end
    % Calculate useful values
    y_conv_speech = fftfilt(y,dry_speech);
    IntLoud_Speech = integratedLoudness(y_conv_speech,fs);
    y_conv_drums = fftfilt(y,dry_drums);
    IntLoud_Drums = integratedLoudness(y_conv_drums,fs);
    % Add row to the table
    delim = strfind(filename,'_');
    Condition = categorical({filename(1:delim(1)-1)});
    Room = categorical({filename(delim(1)+1:delim(2)-1)});
    NewRow = table(Condition,Room,IntLoud_Speech,IntLoud_Drums,NaN,NaN,0,NaN,{y});
    NewRow.Properties.VariableNames = columns;
    T = [T; NewRow];
end

%% Calculate corrections

% First, DRR correction calculated in step 1
T.Correction_DRR(T.Room=='Library') = DRR_adj_lib;
T.Correction_DRR(T.Room=='Trapezoid') = DRR_adj_trap;

% Second, get the level correction from step 2
corr_speech_lib = DRR_adj_lib + T.IntLoud_Speech(T.Room=='Library' & T.Condition == '4OA')-T.IntLoud_Speech(T.Room=='Library');
corr_speech_trap = DRR_adj_trap + T.IntLoud_Speech(T.Room=='Trapezoid' & T.Condition == '4OA')-T.IntLoud_Speech(T.Room=='Trapezoid');

corr_drums_lib = DRR_adj_lib + T.IntLoud_Drums(T.Room=='Library' & T.Condition == '4OA')-T.IntLoud_Drums(T.Room=='Library');
corr_drums_trap = DRR_adj_trap + T.IntLoud_Drums(T.Room=='Trapezoid' & T.Condition == '4OA')-T.IntLoud_Drums(T.Room=='Trapezoid');

T.Correction_IntLoudAvg(T.Room=='Library') = mean([corr_speech_lib,corr_drums_lib],2);
T.Correction_IntLoudAvg(T.Room=='Trapezoid') = mean([corr_speech_trap,corr_drums_trap],2);

%% Additional corrections based on perceptual tuning (particularly RVL)
% NOTE: for some reason, playing a stimulus through RVL sounds quieter than
% the convolution of the same stimulus with the RVL IR. This suggests that
% there may some non-linearity in the toolkit test app. In any case, we can
% correct this issue by performing some perceptual tuning

% The following values were obtaining by perceptual tuning using the
% PairedComp Max patcher, simulating the test conditions.
percepRVLcorr_lib = 4;
percepRVLcorr_trap = 5;

% Fill the values for RVL conditions in the tables. All others are 0.
T.Correction_Perceptual(T.Room=='Library'&T.Condition=='RVL') = percepRVLcorr_lib;
T.Correction_Perceptual(T.Room=='Trapezoid'&T.Condition=='RVL') = percepRVLcorr_trap;

%% Finally, add the corrections together and show the table
T.Correction_Total = T.Correction_DRR + T.Correction_IntLoudAvg + T.Correction_Perceptual;

% Show table
T = sortrows(T,'Room','ascend'); % sort by Room
disp(T)