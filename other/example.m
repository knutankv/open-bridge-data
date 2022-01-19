clear all

tmp = load('test-data.mat');



recording_object = bdcreate.create_sharable_recording(tmp.recording, samplerate);
recording_struct = bdcreate.recobj2struct(recording_object);
recording = recording_struct;

save('rec.mat','recording','-v6')