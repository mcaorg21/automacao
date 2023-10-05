

class RoboLogDao:
    def __init__(self, **kwargs):
        self.fk_idRobo = kwargs.get("fk_idRobo")
        self.dataConsulta = kwargs.get("dataConsulta")
        self.fk_idContrato = kwargs.get("fk_idContrato")
        self.fk_idSolicitacao = kwargs.get("fk_idSolicitacao")
        self.dataFim = kwargs.get("dataFim")
        self.status = kwargs.get("status")
        self.log = kwargs.get("log")

    def __repr__(self):
        return (f"RoboLogDao(fk_idRobo: {self.fk_idRobo}, "
                f"dataConsulta: {self.dataConsulta}, status: {self.status})")
