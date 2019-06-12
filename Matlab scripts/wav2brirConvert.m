%   Convert of wav set to BRIR files
% 
%   Author: David Poirier-Quinot, 
%   Dyson School of Design Engineering, Imperial College of London

clear all

% Set current folder to script's location
cd(fileparts(mfilename('fullpath'))); 

% Get IOs paths
root_path = pwd;
dirName_brir_in = fullfile(root_path,'in');
dirName_brir_out = fullfile(root_path,'out');
dirList_room = getListofDir(dirName_brir_in);

% LOAD WAV
for roomID = 1:length(dirList_room);

    % Get BRIR set list in current room
    dirName_brir = fullfile(dirName_brir_in, dirList_room(roomID).name);
    fprintf('reading room directory: \t %s \n', dirName_brir);    
    fileList_brir = getListofFiles(dirName_brir, '.wav');
    
    % prepare BRIR struct
    l_brir_S = struct();
    l_brir_S.type_s = 'BRIR';
    % l_brir_S.azim_v = deg2rad([0 180 270 90]);
    % l_brir_S.elev_v = deg2rad([0 0 0 0]);
    l_brir_S.azim_v = [];
    l_brir_S.elev_v = [];
    l_brir_S.rcv_pos = [0 0 0];
    l_brir_S.rcv_look = [1 0 0];
    l_brir_S.sampling_hz = 44100;
    l_brir_S.content_m = [];
    r_brir_S = l_brir_S;
    
    for k = 1 : length(fileList_brir) % for each BRIR set in current room
        
        % Load wav file
        index = k;
        name = fileList_brir(index).name;
        fileName = fullfile(dirName_brir, fileList_brir(index).name);
        [y,Fs] = audioread(fileName);
        fprintf('\t -> loading wav set: \t %s \n', fileList_brir(index).name);   
        
        % extract azim / elev values (warning, based on naming convention)
        azFile = str2double(name(strfind(name, '_')+1:strfind(name, 'Az')-1));
        l_brir_S.azim_v(k) = azFile;
        ind = strfind(name, '-');
        elFile = str2double(name(ind(end)+1:strfind(name, 'El')-1));
        l_brir_S.elev_v(k) = elFile;
        
        % check sampling freq
        if( Fs ~= l_brir_S.sampling_hz ); error('sampling freq mismatch'); end
        
        % save to brir struct
        l_brir_S.content_m(k,:) = y(:,1).';
        r_brir_S.content_m(k,:) = y(:,2).';

    end
    
    % save output brir file
    brirName_out = [fullfile(dirName_brir_out, dirList_room(roomID).name) '.mat' ];    
    save(brirName_out, 'l_brir_S', 'r_brir_S');
    fprintf('++ created brir set: \t %s \n', brirName_out);
    
    % debug plot
%     for i = 1:size(l_brir_S.content_m,1);
%         subplot(131),plot(l_brir_S.content_m(i,:)+i); hold on
%         subplot(132),plot(r_brir_S.content_m(i,:)+i); hold on
%     end
%     subplot(131), hold off, subplot(132), hold off
%     [x,y,z] = sph2cart(deg2rad(l_brir_S.azim_v), deg2rad(l_brir_S.elev_v), 1);
%     subplot(133), plot3(x, y, z, '.', 'MarkerSize', 30); grid on;
%     input('');
    
    
end