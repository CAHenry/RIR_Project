function dirList_out = getListofDir(dirName)
% get list of directories in dirName (but for ., .., etc.)

% get list of elements in dirName
dirList = dir(dirName);
dirList_out = dirList;
offset = 0;

% remove unwanted elements (., .., and non directories)
for i=1:length(dirList);
    if ~dirList(i).isdir || strcmpi(dirList(i).name, '.') || strcmpi(dirList(i).name, '..');
        dirList_out(i-offset) = [];
        offset = offset + 1;
    end
end