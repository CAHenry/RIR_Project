
% Take kemar BRIRs and make SOFA files to use in the 3DTI toolkit

% NOTE: the files in the 'in' folder are the same as the ones in the
% RecordedImpulse folder but I changed the names according to the
% convention needed for the wav2brirConvert function. HOWEVER, I am not
% sure if I used the correct Azimuth and Elevation (e.g., I translated our
% 0,90,180,270 degrees directly to Azimuth -- maybe the sign is wrong? --
% and for the Elevation I did top=90, bottom=270). Verify that it's correct
% via listening tests

% NOTE: the debug plots at the end of wav2brirConvert show that the source
% positions have the correct distribution (front/back/L/R/top/bottom) but
% maybe the sides are flipped or something so keep this in mind

% Convert wav to mat file
wav2brirConvert(); % NOTE: comment out if the mat files are already generated

% Loop through all the output files
% filenames = {'Library','Trapezoid'};
filenames = getDirList('out');

% NORMALIZATION: BRIRs were normalized according to pilot tests. Values are
% as follows (in dB). Library first, trapezoid second.
normvalues_db = [-8.5496 -4.8411]; % these are for the 24bit kemar recordings without ear canal
% normvalues_db = [-8.114+1.6663-2+11.606-6,-6.4392+1.6607-4+13.575-6-2.1922]; % these are for the 24bit eigen recordings

for i=1:length(filenames)
    
    % Load file
    name = filenames{i};
    load(['out/',name],'l_brir_S','r_brir_S')
    
    % Create the IR
    L = l_brir_S.content_m;
    R = r_brir_S.content_m;
    IR = [reshape(L,size(L,1),1,size(L,2)),reshape(R,size(R,1),1,size(R,2))];
    
    % Normalisation
    if contains(name,'Library')
        roomname = 'Library';
        title = 'Large room (library) reverb for 6 virtual loudspeakers';
        comment = 'BRIR for the Dyson Building Library at Imperial College';
        normvalue_db = normvalues_db(1);
    elseif contains(name,'Trapezoid')
        roomname = 'Trapezoid';
        title = 'Small room (trapezoid) reverb for 6 virtual loudspeakers';
        comment = 'BRIR for the meeting room "Trapezoid 3" at the Dyson Building, Imperial College';
        normvalue_db = normvalues_db(2);
    else
        error('Name is not Library or Trapezoid!');
    end
    normvalue = 10.^(normvalue_db/20);
    IR = IR.*normvalue;

    % Fill in the data struct
    data = struct();
    data.IR = IR;
    data.SamplingRate = l_brir_S.sampling_hz;
    data.SamplingRate_Units = 'hertz';
    data.Delay = [0,0];
    
    % Load 3DTI BRIR and replace the needed parts
    S = SOFAload('ExampleBRIRs/3DTI_BRIR_large_44100Hz.sofa');

    % Change relevant bits
    S.GLOBAL_DateCreated = '3 May 2019';
    S.GLOBAL_DateModified = '3 May 2019';
    S.GLOBAL_Title = title;
    S.GLOBAL_AuthorContact = 'Isaac Engel (isaac.engel@imperial.ac.uk)';
    S.GLOBAL_Comment = comment;
    S.GLOBAL_History = 'version 1.0';
    S.GLOBAL_Organization = 'Imperial College London';
    S.GLOBAL_ListenerShortName = 'KEMAR dummy head with KB0065 and KB0066 pinnae';
    S.GLOBAL_SourceDescription='Genelec 8030';
    
    Az = l_brir_S.azim_v';
    El = l_brir_S.elev_v';
    R = repmat(1.2,length(Az),1);
    S.SourcePosition = [Az,El,R];
    S.Data = data;
    
%     % Make struct to be saved as SOFA   
%     S = struct();
% 
%     % Add metadata
%     S.GLOBAL_SOFAConventions = 'SimpleFreeFieldHRIR';
%     S.GLOBAL_Conventions = 'SOFA';
%     S.GLOBAL_Version = '1.0';
%     S.GLOBAL_SOFAConventionsVersion = '1.0';
%     S.GLOBAL_APIName = 'ARI SOFA API for Matlab/Octave';
%     S.GLOBAL_APIVersion = '1.0.1';
%     S.GLOBAL_AuthorContact = 'Isaac Engel (isaac.engel@imperial.ac.uk)';
%     S.GLOBAL_DataType = 'FIR';
%     S.GLOBAL_License = 'No license provided, ask the author for permission';
%     S.GLOBAL_Organization = '';
%     S.GLOBAL_RoomType = 'free field';
%     S.GLOBAL_DateCreated = '3 May 2019';
%     S.GLOBAL_DateModified = '3 May 2019';
%     S.GLOBAL_Title = 'Library reverb for 6 virtual loudspeakers';
%     
%     % Add data
%     S.ListenerPosition_Type = 'cartesian';
%     S.API = struct();
%     S.ListenerPosition = [0,0,0];
%     S.Data = data;

    % Save to SOFA file
    SOFAsave(['SOFAfiles/BRIR_',roomname,'_',num2str(data.SamplingRate),'Hz.sofa'],S);
end

clear title

disp('Finished!')