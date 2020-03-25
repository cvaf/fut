from datetime import datetime
date = datetime.now()

ckpt_date = 'weights' + str(int(date.month * 100) + int(date.day))
ckpt_name = ckpt_date + '.{epoch:02d}-{val_loss:.2f}.hdf5'
ckpt_path = 'models/checkpoints/' + ckpt_name
CHECKPOINT_DICT = {'folder': 'models/checkpoints',
                   'name': ckpt_name,
                   'path': ckpt_path}