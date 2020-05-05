from datetime import datetime
date = datetime.now()


ckpt_date = 'weights' + str(datetime.now().strftime('%m%d'))
ckpt_name = ckpt_date + '.{epoch:02d}-{val_loss:.2f}.hdf5'
ckpt_path = 'models/checkpoints/' + ckpt_name
CHECKPOINT_DICT = {'folder': 'models/checkpoints',
                   'name': ckpt_name,
                   'path': ckpt_path}