% ELE 224L - Experiment 1 - Section 1.2
% I-V characteristic of the diode equation, -1 V <= VD <= 1 V
clear; clc; close all;

VT = 0.026;      % thermal voltage (V)
IS = 20e-15;     % saturation current (A)
n  = 1;          % ideality factor

VD = linspace(-1, 1, 2001);          % diode voltage vector (V)
ID = IS .* (exp(VD ./ (n*VT)) - 1);  % diode equation, Eq. (1)

figure('Name', 'Diode I-V');
subplot(1,2,1);
plot(VD, ID*1e3, 'b', 'LineWidth', 1.5); grid on;
xlabel('V_D (V)'); ylabel('I_D (mA)');
title('Linear scale (zoomed)');
ylim([-1 20]); xlim([-1 1]);

subplot(1,2,2);
semilogy(VD, abs(ID), 'b', 'LineWidth', 1.5); grid on;
xlabel('V_D (V)'); ylabel('|I_D| (A)');
title('Semilog scale');

% numerical check values printed to the command window
VDchk = [-1 0 0.5 0.6 0.7];
IDchk = IS .* (exp(VDchk ./ (n*VT)) - 1);
for k = 1:numel(VDchk)
    fprintf('VD = %5.2f V  ->  ID = %.6e A\n', VDchk(k), IDchk(k));
end
