
% Proof of concept that the ambisonic 4th order recording has all the info
% from the previous orders. Also useful for us to verify that the
% eigenstudio outputs are consistent

% Read all the files
[zeroth,fs] = audioread('ambisonic/Library_Eigenmike_0_Ambi0OA.wav');
first = audioread('ambisonic/Library_Eigenmike_0_Ambi1OA.wav');
second = audioread('ambisonic/Library_Eigenmike_0_Ambi2OA.wav');
third = audioread('ambisonic/Library_Eigenmike_0_Ambi3OA.wav');
fourth = audioread('ambisonic_minus12db/Library_Eigenmike_0_Ambi4OA.wav');

% Crop all to the same length (in this case, 1 second)
zeroth = zeroth(1:fs,:);
first = first(1:fs,:);
second = second(1:fs,:);
third = third(1:fs,:);
fourth = fourth(1:fs,:);

% Plot the differences between the 4th order channels in the previous ones.
% They should be zero
d0 = abs(fourth(:,1)-zeroth);
d1 = abs(fourth(:,1:4)-first);
d2 = abs(fourth(:,1:9)-second);
d3 = abs(fourth(:,1:16)-third);
dmax = [max(d0),max(max(d1)),max(max(d2)),max(max(d3))];
fprintf('The maximum absolute differences between 4th order and the other orders are: %0.2f (0th), %0.2f (1st), %0.2f (2nd), %0.2f (3rd)\n',dmax);

db0 = db((rms(zeroth)));
db1 = db((rms(first)));
db2 = db((rms(second)));
db3 = db((rms(third)));
db4 = db((rms(fourth)));

dd0 = db0-db4(1);
dd1 = mean(db1-db4(1:4));
dd2 = mean(db2-db4(1:9));
dd3 = mean(db3-db4(1:16));

fprintf('The RMS differences between 4th order and the other orders are: %0.2f (0th), %0.2f (1st), %0.2f (2nd), %0.2f (3rd)\n',dd0,dd1,dd2,dd3);


% figure, plot(d0)
% figure, plot(d1)
% figure, plot(d2)
% figure, plot(d3)