path = '.';
sensorNames = {'1S' '1N' '2S' '2N' '3S' '3N' '4S' '4N' '5S' '5N' '6S' '6N' '7S' '7N' 'A1' 'A2' 'A3' 'A4' 'A5' 'W1' 'W2' 'W3' 'W4' 'W5' 'W6' 'W1b' 'W2b' 'W3b' 'W4b' 'W5b' 'W6b'  'GNSS'};
components = {1:3, 1:3, 1:3,  1:3, 1:3, 1:3, 1:3, 1:3, 1:3, 1:3, 1:3, 1:3, 1:3, 1:3, 1:4, 1:4, 1:4, 1:4, 1:4, 1:2, 1:2, 1:2, 1:2, 1:2, 1:2, 1:2,  1:2,  1:2,  1:2,  1:2,  1:2,   1:3};

acc = {'x', 'y', 'z'};
gnss = {'x', 'y', 'z'};
wave = {'h', 'mh'};
wind = {'angle', 'U', 'w', 'T'};

component_names = {acc; acc; acc; acc; acc; acc; acc; acc; acc; acc; acc; acc; acc; acc;
                   wind; wind; wind; wind; wind; wave; wave; wave; wave; wave; wave; wave; wave; wave; wave; wave; wave; gnss};

statistics = folder_statistics(path, sensorNames, component_names);

save(fullfile('stats.mat'),'statistics')