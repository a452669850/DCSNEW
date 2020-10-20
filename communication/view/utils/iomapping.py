from communication.model import VarModel


class IOMapping:
    current_value = None

    @classmethod
    def setup_Current(cls):
        cls.current_value = {var.sig_name: None for var in VarModel.select()}

    @classmethod
    def set_Current(cls, name):
        from communication import skio
        cls.current_value[name] = skio.read(name)

    @classmethod
    def updata_varmodel(cls, lis, id):
        for i in lis:
            if i[1] == 'Sig_name':
                VarModel.update(sig_name=i[0]).where(VarModel.id == id).execute()
            if i[1] == 'Sig_type':
                VarModel.update(sig_type=i[0]).where(VarModel.id == id).execute()
            if i[1] == 'Slot':
                VarModel.update(slot=i[0]).where(VarModel.id == id).execute()
            if i[1] == 'Channel':
                VarModel.update(channel=i[0]).where(VarModel.id == id).execute()
