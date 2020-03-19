function plotHOA(hoasig,newfigure)
% Directional plot (pressure vs time vs azimuth)
% Input:
%   hoasig = nsamples x nchannels
%   newfigure (true)

% TODO: plot time intervals for precedence effect and stuff

if ~exist('newfigure','var')
    newfigure = true;
end

len = round(0.03*44100); % plot only the first 30ms
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
dbsig = db(p_t);
dbsig(dbsig<-60) = -60;
if newfigure
    figure
end
s = surf(dir_ev(:,1),tvec,dbsig);
colormap(flipud(gray))
view(2) % vertical view
s.EdgeColor = 'none'; % remove surface lines
set(gca,'YDir','reverse')
set(gca,'XDir','reverse')
%             caxis([-1 1])
%             zlim([-1 1])
caxis([-50 0])
zlim([-60 0])
xlim([-180 180])
xlabel('Az. [deg]')
ylabel('t [s]')