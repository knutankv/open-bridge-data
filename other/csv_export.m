load('BergsoysundExampleRecording_10Hz')

data = cell2mat({recording.sensor.data});
comp_units = {};
sensor_names = {recording.sensor.sensor_name};

wave_sensor_ix = find(contains(sensor_names,'W'));
for s = wave_sensor_ix
    recording.sensor(s).component_units = {'m' 'm'};
end


for s = 1:14
    sensor_names{s} = ['acc_' sensor_names{s}];
end

sensor_names{15} = 'GNSS';

count = 0;
for s = 1:length(sensor_names)
    units = recording.sensor(s).component_units;
    comps = recording.sensor(s).component_names;
    for c=1:length(comps)
        count = count+1;
        full_name{count} = [sensor_names{s}, '_', comps{c}, ' [', units{c}, ']'];
    end
end

%% XLSX
filename = 'BergsoysundExampleRecording_10Hz.xlsx';

data_cells = num2cell(data);     %Convert data to cell array
output_matrix=[full_name; data_cells];     %Join cell arrays
xlswrite(filename,output_matrix);     %Write data and both headers

%% Write to csv
count = 0;
full_name = {};
for s = 1:length(sensor_names)
    comps = recording.sensor(s).component_names;
    for c=1:length(comps)
        count = count+1;
        full_name{count} = [sensor_names{s}, '_', comps{c}];
    end
end
filename = 'BergsoysundExampleRecording_10Hz.csv';
writetable(array2table(data, 'VariableNames', full_name), filename);