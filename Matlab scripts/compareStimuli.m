
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

rootDir = 'Stimuli/';
% recordingsDir = [rootDir,'3DTI recordings 19 august/TakeFive nodirect/'];
% recordingsDir = [rootDir,'Convolved stimuli 19 august calibrated/TakeFive_Drums_Dirac1 nodirect/'];
recordingsDir = [rootDir,'3DTI recordings 19 august calibrated/'];

%% Level normalisation

disp('Level normalisation')
disp('-------------------')

filenames = getDirList(recordingsDir);
nfiles = length(filenames);

% Table to store the data
columns = {'Condition','Room','Stimulus','IntLoud','Correction'};
T = table({},{},{},[],[],'VariableNames',columns);

% Iterate through all the files in the folder and fill the table
disp('Reading audio files...')
for filename = filenames 
    filename = filename{1};
    % Read audio file
    filepath = [recordingsDir,filename];
    [y,fs_temp] = audioread(filepath);
    if fs_temp ~= fs
        error('Sampling frequency mismatch!');
    end
    % Calculate useful values
    IntLoud = integratedLoudness(y(1:5*fs,:),fs);
    % Add row to the table
    delim = strfind(filename,'_');
    Condition = categorical({filename(1:delim(1)-1)});
    Room = categorical({filename(delim(1)+1:delim(2)-1)});
    Stimulus = categorical({filename(delim(2)+1:end-4)});
    NewRow = table(Condition,Room,Stimulus,IntLoud,NaN);
    NewRow.Properties.VariableNames = columns;
    T = [T; NewRow];
    
    % Plot pwelch (optional)
%     figure
%     window = 512; % window length for pwelch
%     [pxx,w] = pwelch(y,window);
%     ff = w*fs/(2*pi);
%     ind1 = find(ff>20); ind1 = ind1(1);
%     ind2 = find(ff>20000); ind2 = ind2(1);
%     %pxx = pxx./rms(pxx(ind1:ind2,:));
%     semilogx(ff,db(pxx)), grid on
%     xlim([20,fs/2])
%     xlabel('f [Hz]'), ylabel('Magnitude [dB]')
%     title(sprintf('Power spectral density (pwelch) - %s, %s, %s',Condition,Room,Stimulus)) 
end

% Calculate correction
% T.Correction(T.Room=='Library' & T.Stimulus=='TakeFive') = T.IntLoud(T.Room=='Library' & T.Stimulus=='TakeFive' & T.Condition == '1OA')-T.IntLoud(T.Room=='Library' & T.Stimulus=='TakeFive');
% T.Correction(T.Room=='Trapezoid' & T.Stimulus=='TakeFive') = T.IntLoud(T.Room=='Trapezoid' & T.Stimulus=='TakeFive' & T.Condition == '1OA')-T.IntLoud(T.Room=='Trapezoid' & T.Stimulus=='TakeFive');

% Show table
T = sortrows(T,'Stimulus','ascend');
T = sortrows(T,'Room','ascend'); % sort by Room
disp(T)