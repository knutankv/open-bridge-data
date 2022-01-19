function [ statistics ] = folder_statistics(path, sensorNames, component_names)
% Updated 2021-11-02.

componentCount = cellfun(@(x) length(x), component_names);
tmp = dir(fullfile(path, '*.mat'));
files = {tmp.name};

for f = 1:length(files)
    importedData = load(fullfile(path, files{f}),'recording');
    recording = importedData.recording;
    
    if isempty(sensorNames)
        sensorNames = recording.sensor_names;
    end
    
    sensorNamesInRecording = recording.sensor_names;
    [~, presentSensorIxStat, presentSensorIxRec] = intersect(sensorNames, sensorNamesInRecording);
    
    for s = 1:length(sensorNames)       
       
        if any(presentSensorIxStat==s)
            statistics.sensor(s).std(f, :) = std(recording.sensor(presentSensorIxRec(presentSensorIxStat==s)).data);
            statistics.sensor(s).mean(f, :)= mean(recording.sensor(presentSensorIxRec(presentSensorIxStat==s)).data);
            statistics.sensor(s).swh(f, :) = 4*std(recording.sensor(presentSensorIxRec(presentSensorIxStat==s)).data);
        else
            statistics.sensor(s).std(f,:) = nan([componentCount(s), 1]);
            statistics.sensor(s).mean(f,:) = nan([componentCount(s), 1]);
            statistics.sensor(s).swh(f,:) = nan([componentCount(s), 1]);
        end
        
        statistics.recording{f} = files{f};
    end
    
% Assign global sensor / component info
for s = 1:length(sensorNames)
    statistics.sensor(s).sensor_name = sensorNames{s};
    statistics.sensor(s).component_names = component_names{s};
end

    
end

