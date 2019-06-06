% requires polarch-Higher-Order-Ambisonics-39eea5a


hoasig = audioread('C:\Users\craig\Desktop\test_right_direct.wav');
[~, ls_dirs_rad] = platonicSolid('dodecahedron');
ls_dirs = ls_dirs_rad*180/pi;

% ls_dirs = [0    0
%            90   0
%            180  0
%            270  0
%            0    90
%            0    -90];

% dodecahedral setup
ls_num = size(ls_dirs,1);
% get order (3 in this case)
N = floor(sqrt(ls_num) - 1);
% get a projection (sampling) decoder
D_sad = ambiDecoder(ls_dirs, 'sad', 0, N);
% decode signals
lssig = decodeHOA_N3D(hoasig, D_sad);

audiowrite('C:\Users\craig\Documents\RIR_Project\Audio_files\Impulses\Library\Eigenmike\ambisonic_decoded\Test_270_direct.wav', lssig, 44100)