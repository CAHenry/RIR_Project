function plotHOA2(hoasig)
% Directional plot (pressure vs time vs azimuth)
% This version uses a method inspired by [1]
%   hoasig = nsamples x nchannels
%
% References:
%   [1] Benoit Alary et al, "Assessing the anisotropic features of spatial
%   impulse responses", EAA Spatial Audio Sig. Proc. Symp., Paris 2019

% TODO: plot time intervals for precedence effect and stuff

tmix = 0; % TODO: in [1] they like to plot only reverb, while we may want to plot everything in which case, tmix=0
tnoise = 0.03; % TODO: this should be calculated properly so the noise floor doesn't polute the results

len = round(tnoise*44100); % plot only the first 30ms
tvec = (0:len-1)/44100;

% Get pressure at the center point according to eq6.13 from [1]
nfft = 2^nextpow2(size(hoasig,1));
b_W = fft(hoasig,nfft);
b_W = b_W(1:end/2+1,:); % keep only up to Nyquist frequency

nchannels = size(hoasig,2);
N = sqrt(nchannels)-1;

dir_ev = [linspace(-180,180,180)',zeros(180,1)]; % directions to be evaluated
Y_ev = getRSH(N,dir_ev); % encode in the SH domain

j_vec=1; % this would be the Bessel function, but doesn't apply here because we are evaluating at the center point, not a sphere     

p = b_W.*j_vec*Y_ev; % get vector of pressure values

p = [p; flipud(conj(p(2:end-1,:)))]; % reconstruct full spectrum
p(1,:) = real(p(1,:)); % f=0 and f=Nyquist should be real for the ifft to be real
p(end/2+1,:) = real(p(end/2+1,:));

p_t = ifft(p); % Convert to the time domain 
p_t = p_t(1:len,:); % keep the first 'len' samples
%             norm_value = mean(rms(p));
%             fprintf('Normalizing by %0.2f\n',norm_value);
%             p_t = p_t./norm_value;
%             fprintf('average rms = %0.3f\n',mean(rms(p_t)));

% NOTE: I think this p_t is the signal y in [1] because they say that the
% "beamforming weight vector" d is all ones. Would have to confirm this,
% though.

ind = find(tvec>=tmix); ind = ind(1);
EDC = cumsum(p_t(ind:end,:).^2,'reverse');
EDC_db = db(EDC);
EDC_dbmean = mean(EDC_db,2);
EDD_db = EDC_db-repmat(EDC_dbmean,1,size(EDC_db,2));

% dbsig(dbsig<-60) = -60;
figure, s = surf(dir_ev(:,1),tvec,EDC_db);
colormap(flipud(gray))
view(2) % vertical view
s.EdgeColor = 'none'; % remove surface lines
set(gca,'YDir','reverse')
set(gca,'XDir','reverse')
%             caxis([-1 1])
%             zlim([-1 1])
caxis([-100 0])
zlim([-100 0])
xlim([-180 180])
xlabel('Azimuth [degrees]')
ylabel('t [s]')
title('EDC')

figure, s = surf(dir_ev(:,1),tvec,EDD_db);
% colormap(flipud(gray))
colormap(redblue)
view(2) % vertical view
s.EdgeColor = 'none'; % remove surface lines
set(gca,'YDir','reverse')
set(gca,'XDir','reverse')
%             caxis([-1 1])
%             zlim([-1 1])
caxis([-20 20])
zlim([-30 30])
xlim([-180 180])
xlabel('Azimuth [degrees]')
ylabel('t [s]')