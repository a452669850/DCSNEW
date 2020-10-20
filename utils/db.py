#!/usr/bin/env python
# -*- coding: utf-8 -*-

from procedure.manage_procedure.models import (
    Procedure, UsecaseGroup, Usecase,
    RunResult, InitProcedure, StatisticalReport,
    LoopRunResult
)

from rbac_permission_or_trendgroup_management.models import (
    User, Group, UserGroup, Operation,
    GroupOperatePermission,
)

from rbac_permission_or_trendgroup_management.trend_models import (
    TrendGroup, TrendPoint, TrendGroupXrefPoint
)

from dcs_io.model import PointModel, NetworkConfig, PointGroup, ModbusAddress


def initDatabase(db):
    modelsArr = [
        User, Group, UserGroup, Operation, GroupOperatePermission, LoopRunResult,
        TrendGroup, TrendPoint, TrendGroupXrefPoint,
        Procedure, UsecaseGroup, Usecase, RunResult, InitProcedure, StatisticalReport,
        PointModel, NetworkConfig, ModbusAddress, PointGroup, PointGroup.points.get_through_model()
    ]

    db.connect()
    db.create_tables(modelsArr, safe=True)
