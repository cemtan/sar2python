#!/usr/bin/python3

import argparse
import os
import pprint
import re
import subprocess
from copy import deepcopy

import exrex
import requests
import sys
import xlrd
import xlwt


class TenantInfo:
    def __init__(self, tenant_name='', ca_id='', domain='', asms=[], users=[], owner={}):
        self.tenant_name = tenant_name
        self.ca_id = ca_id
        self.domain = domain
        self.asms = asms
        self.users = users
        self.owner = owner
        self.tenant_id = ''

    def __str__(self):
        return ("Tenant Name (Sheet): {}, \n"
                "CA ID: {}, Domain: {}, \n"
                "Users: \n{}\n, ASMs: {}\n, Owner: {}").format(
            self.tenant_name, self.ca_id, self.domain,
            pprint.pformat(self.users), self.asms, self.owner, self.tenant_id
        )


def includeAsm(asmEmail):
    try:
        FileExclude = open("excludeUsers.txt", "r")
        exclude = FileExclude.read()
        FileExclude.close()
        if asmEmail in exclude:
            return False
        else:
            return True
    except:
        return True


def includeTenant(tenantCaId):
    try:
        FileExclude = open("excludeTenants.txt", "r")
        exclude = FileExclude.read()
        FileExclude.close()
        if tenantCaId in exclude:
            return False
        else:
            return True
    except:
        return True


def getDomain(tenantDomain, searchIn=False):
    caIDArray = []
    for domainrow in range(SheetUser.nrows):
        searchDomain = SheetUser.cell(domainrow, ColumnDomain).value.strip()
        if '@' in searchDomain:
            searchDomain = searchDomain.split('@')[1]
        if (tenantDomain.lower() == searchDomain.lower() and not searchIn) or (
                tenantDomain.lower() in searchDomain.lower() and searchIn):
            for row in range(SheetCaOwner.nrows):
                if SheetCaOwner.cell(row, ColumnCaIdofCA).value.strip() == SheetUser.cell(domainrow,
                                                                                          ColumnCaIdofUL).value.strip():
                    if SheetUser.cell(domainrow, ColumnCaIdofUL).value.strip() not in caIDArray:
                        tenant = getTenantInfo(tenantName=SheetCaOwner.cell(row, ColumnTenantName).value.strip(),
                                      setexact='exact')
                        tenant.domain = searchDomain
                        caIDArray.append(SheetUser.cell(domainrow, ColumnCaIdofUL).value.strip())
                        return tenant
    return None


def getTenantInfo(tenantName, notLogged=None, setexact=None):
    userArray = []
    asmArray = []
    okasmArray = []
    details = TenantInfo()
    for row in range(SheetCaOwner.nrows):
        if setexact:
            searchAlg = tenantName == SheetCaOwner.cell(row, ColumnTenantName).value.strip()
        else:
            searchAlg = tenantName.lower() in SheetCaOwner.cell(row, ColumnTenantName).value.strip().lower()
        if str(searchAlg) == 'True':
            if not notLogged:
                print('Tenant Information:')
                print('--------------------------------')
                print('Tenant NAME        :', SheetCaOwner.cell(row, ColumnTenantName).value.strip())
                tenantCaId = SheetCaOwner.cell(row, ColumnCaIdofCA).value.strip()
                print('CA ID              : ' + tenantCaId)
                print('Portal OWNER       : ' + SheetCaOwner.cell(row, ColumnPortalOwner).value)
                print('Portal Owner EMAIL : ' + SheetCaOwner.cell(row, ColumnPortalOwnerEmail).value)
                details.tenant_name = tenantName
                details.ca_id = SheetCaOwner.cell(row, ColumnCaIdofCA).value.strip()
                details.owner = {'name': SheetCaOwner.cell(row, ColumnPortalOwner).value.strip(),
                                 'email': SheetCaOwner.cell(row, ColumnPortalOwnerEmail).value.strip()}

                for row in range(SheetUser.nrows):
                    if tenantCaId == SheetUser.cell(row, ColumnCaIdofUL).value.strip():
                        details.domain = SheetUser.cell(row, ColumnDomain).value.strip()
                        print('Domain             : ' + details.domain)
                        break

                for portalrow in range(SheetPortal.nrows):
                    if tenantCaId == SheetPortal.cell(portalrow, ColumnCaIdofPortal).value.strip():
                        print('FC Account ID      : ' + SheetPortal.cell(portalrow, ColumnPortalId).value.strip())

                for row in range(SheetBilling.nrows):
                    if tenantCaId == SheetBilling.cell(row, ColumnCaIdofBilling).value.strip():
                        print('Count of FC Account: ' + str(SheetBilling.cell(row, ColumnBilling).value))

                print('\nUser Information:')
                print('--------------------------------')

                count = 1

                for row in range(SheetUser.nrows):
                    if tenantCaId == SheetUser.cell(row, ColumnCaIdofUL).value.strip():
                        if SheetUser.cell(row, ColumnUserEmail).value not in userArray:
                            print('USER ' + str(count))
                            print('+++++++++++++++')
                            print('User NAME          : ' + SheetUser.cell(row, ColumnUserName).value)
                            print('User EMAIL         : ' + SheetUser.cell(row, ColumnUserEmail).value)
                            count += 1
                            details.users.append({'name': SheetUser.cell(row, ColumnUserName).value.strip(),
                                                  'email': SheetUser.cell(row, ColumnUserEmail).value.strip()})
                            userArray.append(SheetUser.cell(row, ColumnUserEmail).value)

                print('\nASM Information:')
                print('--------------------------------')

                count = 1

                for row in range(SheetAsm.nrows):
                    if tenantCaId == SheetAsm.cell(row, ColumnCaIdofASM).value.strip() and includeAsm(
                            SheetAsm.cell(row, ColumnASMEmail).value):
                        logged = 0
                        if SheetAsm.cell(row, ColumnASMEmail).value not in asmArray:
                            if SheetAsm.cell(row, ColumnASMEmail).value.strip() in contentAsm:
                                logged = 1
                                asmArray.append(SheetAsm.cell(row, ColumnASMEmail).value)
                            if logged == 1:
                                print('ASM ' + str(count), '- Logged')
                            else:
                                print('ASM ' + str(count))
                            print('+++++++++++++++')
                            print('Asm NAME           : ' + SheetAsm.cell(row, ColumnASMName).value)
                            print('Asm SURNAME        : ' + SheetAsm.cell(row, ColumnASMSurname).value)
                            print('Asm EMAIL          : ' + SheetAsm.cell(row, ColumnASMEmail).value)
                            count += 1
                print('-' * 70)
                details.asms = asmArray
            else:
                print(SheetCaOwner.cell(row, ColumnTenantName).value.strip())
                tenantCaId = SheetCaOwner.cell(row, ColumnCaIdofCA).value.strip()
                print('-' * 50)
                for arow in range(SheetAsm.nrows):
                    if tenantCaId == SheetAsm.cell(arow, ColumnCaIdofASM).value.strip() and includeAsm(
                            SheetAsm.cell(arow, ColumnASMEmail).value) and SheetAsm.cell(arow,
                                                                                         ColumnASMEmail).value not in asmArray and SheetAsm.cell(
                        arow, ColumnASMEmail).value.strip() not in contentAsm:
                        print('-', SheetAsm.cell(arow, ColumnASMEmail).value)
    if not details.tenant_name:
        print(f'Unable to find any tenant with the name "{tenantName}"')
    return None if details.tenant_name == '' else details


def getReport():
    rowNum = 1
    nonloggedrowNum = 1
    loggedrowNum = 1
    nonrowNum = 1
    completeNum = 1
    notdoneNum = 1
    pendingNum = 1
    wb = xlwt.Workbook()
    style_bold = xlwt.easyxf('font: bold on, height 260; align: wrap true, horiz left, vert top')
    style_logged = xlwt.easyxf(
        'pattern: pattern solid, fore-colour light_yellow; align: wrap true, horiz left, vert top')
    style_noasm = xlwt.easyxf('pattern: pattern solid, fore-colour gray25; align: wrap true, horiz left, vert top')
    style_complete = xlwt.easyxf(
        'pattern: pattern solid, fore-colour light_green; align: wrap true, horiz left, vert top')
    style_pending = xlwt.easyxf(
        'pattern: pattern solid, fore-colour tan; align: wrap true, horiz left, vert top')
    style_normal = xlwt.easyxf('align: wrap true, horiz left, vert top')
    ws_allAsm = wb.add_sheet('All Tenants')
    ws_completeAsm = wb.add_sheet('GLHC Tenants')
    ws_pendingAsm = wb.add_sheet('Pending Tenants')
    ws_notdoneAsm = wb.add_sheet('Waiting Tenants')
    ws_loggedAsm = wb.add_sheet('All ASMs logged in')
    ws_nonloggedAsm = wb.add_sheet('All ASMs not logged in')
    ws_noAsm = wb.add_sheet('No ASM')
    ws_explanation = wb.add_sheet('Color Codes')
    ws_allAsm.write(0, 0, 'Company Name', style=style_bold)
    ws_allAsm.write(0, 1, 'CA Tenant ID', style=style_bold)
    ws_allAsm.write(0, 2, 'FC Account ID (Biling ID, Portal ID)', style=style_bold)
    ws_allAsm.write(0, 3, 'Status', style=style_bold)
    ws_allAsm.write(0, 4, 'ASMs', style=style_bold)
    ws_completeAsm.write(0, 0, 'Company Name', style=style_bold)
    ws_completeAsm.write(0, 1, 'CA Tenant ID', style=style_bold)
    ws_completeAsm.write(0, 2, 'FC Account ID (Biling ID, Portal ID)', style=style_bold)
    ws_completeAsm.write(0, 3, 'Status', style=style_bold)
    ws_completeAsm.write(0, 4, 'ASMs', style=style_bold)
    ws_pendingAsm.write(0, 0, 'Company Name', style=style_bold)
    ws_pendingAsm.write(0, 1, 'CA Tenant ID', style=style_bold)
    ws_pendingAsm.write(0, 2, 'FC Account ID (Biling ID, Portal ID)', style=style_bold)
    ws_pendingAsm.write(0, 3, 'Status', style=style_bold)
    ws_pendingAsm.write(0, 4, 'ASMs', style=style_bold)
    ws_notdoneAsm.write(0, 0, 'Company Name', style=style_bold)
    ws_notdoneAsm.write(0, 1, 'CA Tenant ID', style=style_bold)
    ws_notdoneAsm.write(0, 2, 'FC Account ID (Biling ID, Portal ID)', style=style_bold)
    ws_notdoneAsm.write(0, 3, 'Status', style=style_bold)
    ws_notdoneAsm.write(0, 4, 'ASMs', style=style_bold)
    ws_nonloggedAsm.write(0, 0, 'Company Name', style=style_bold)
    ws_nonloggedAsm.write(0, 1, 'CA Tenant ID', style=style_bold)
    ws_nonloggedAsm.write(0, 2, 'FC Account ID (Biling ID, Portal ID)', style=style_bold)
    ws_nonloggedAsm.write(0, 3, 'Status', style=style_bold)
    ws_nonloggedAsm.write(0, 4, 'ASMs', style=style_bold)
    ws_loggedAsm.write(0, 0, 'Company Name', style=style_bold)
    ws_loggedAsm.write(0, 1, 'CA Tenant ID', style=style_bold)
    ws_loggedAsm.write(0, 2, 'FC Account ID (Biling ID, Portal ID)', style=style_bold)
    ws_loggedAsm.write(0, 3, 'Status', style=style_bold)  #
    ws_loggedAsm.write(0, 4, 'ASMs', style=style_bold)  #
    ws_noAsm.write(0, 0, 'Company Name', style=style_bold)
    ws_noAsm.write(0, 1, 'CA Tenant ID', style=style_bold)
    ws_noAsm.write(0, 2, 'FC Account ID (Biling ID, Portal ID)', style=style_bold)
    ws_explanation.write(0, 0, 'Header', style=style_bold)
    ws_explanation.write(1, 0, 'Tenant onboarded', style=style_complete)
    ws_explanation.write(2, 0, 'ASM logged in', style=style_logged)
    ws_explanation.write(3, 0, 'ASM does not exist', style=style_noasm)
    ws_explanation.write(4, 0, 'Pending Tenant', style=style_pending)
    ws_allAsm.col(0).width = 256 * 57
    ws_completeAsm.col(0).width = 256 * 57
    ws_pendingAsm.col(0).width = 256 * 57
    ws_notdoneAsm.col(0).width = 256 * 57
    ws_nonloggedAsm.col(0).width = 256 * 57
    ws_loggedAsm.col(0).width = 256 * 57
    ws_noAsm.col(0).width = 256 * 57
    ws_explanation.col(0).width = 256 * 57
    for colNum in {1, 2, 3}:
        ws_allAsm.col(colNum).width = 256 * 46
        ws_completeAsm.col(colNum).width = 256 * 46
        ws_pendingAsm.col(colNum).width = 256 * 46
        ws_notdoneAsm.col(colNum).width = 256 * 46
        ws_loggedAsm.col(colNum).width = 256 * 46
        ws_nonloggedAsm.col(colNum).width = 256 * 46
    for colNum in {1, 2}:
        ws_noAsm.col(colNum).width = 256 * 46
    for row in range(1, SheetCaOwner.nrows):
        if includeTenant(SheetCaOwner.cell(row, ColumnCaIdofCA).value.strip()):
            asmArray = ''
            asmNotLogged = ''
            asmLogged = ''
            tenantCaId = SheetCaOwner.cell(row, ColumnCaIdofCA).value.strip()
            for domainrow in range(SheetUser.nrows):  #
                if tenantCaId == SheetUser.cell(domainrow, ColumnCaIdofUL).value.strip():
                    tenantDomain = SheetUser.cell(domainrow, ColumnDomain).value.strip().lower()
                    if '@' in tenantDomain:
                        tenantDomain = tenantDomain.split('@')[1]
                    break  #
            xlwtout = SheetCaOwner.cell(row, ColumnTenantName).value.strip() + ":" + tenantCaId + ":"
            firstentry = 0
            for portalrow in range(SheetPortal.nrows):
                if tenantCaId == SheetPortal.cell(portalrow, ColumnCaIdofPortal).value.strip():
                    if firstentry == 0:
                        xlwtout = xlwtout + SheetPortal.cell(portalrow, ColumnPortalId).value.strip()
                        firstentry = 1
                    else:
                        xlwtout = xlwtout + "\n" + SheetPortal.cell(portalrow, ColumnPortalId).value.strip()
            for arow in range(SheetAsm.nrows):
                if tenantCaId == SheetAsm.cell(arow, ColumnCaIdofASM).value.strip() and includeAsm(
                        SheetAsm.cell(arow, ColumnASMEmail).value) and SheetAsm.cell(arow,
                                                                                     ColumnASMEmail).value not in asmArray:
                    if SheetAsm.cell(arow, ColumnASMEmail).value.strip() not in contentAsm:
                        asmNotLogged = asmNotLogged + ":" + SheetAsm.cell(arow, ColumnASMEmail).value.strip()
                    elif SheetAsm.cell(arow, ColumnASMEmail).value.strip() in contentAsm:
                        asmLogged = asmLogged + ":" + SheetAsm.cell(arow, ColumnASMEmail).value.strip()
                    asmArray = asmArray + ":" + SheetAsm.cell(arow, ColumnASMEmail).value.strip()
            xlwtoutall = xlwtout + ':Status' + asmArray
            for brow in range(SheetBilling.nrows):
                if tenantCaId == SheetBilling.cell(brow, ColumnCaIdofBilling).value.strip():
                    fcCount = SheetBilling.cell(brow, ColumnBilling).value
            for colNum, cellInfo in enumerate(xlwtoutall.split(':')):
                if colNum == 0:
                    ws_allAsm.col(colNum).width = 256 * 57
                else:
                    ws_allAsm.col(colNum).width = 256 * 46
                if colNum in {0, 1, 2, 3}:
                    if tenantDomain in contentGLHCDomain:
                        if colNum == 3:
                            ws_allAsm.write(rowNum, colNum, 'Done', style=style_complete)
                        else:
                            ws_allAsm.write(rowNum, colNum, cellInfo, style=style_complete)
                    elif tenantDomain in contentPendingDomain:
                        if colNum == 3:
                            ws_allAsm.write(rowNum, colNum, 'Pending', style=style_pending)
                        else:
                            ws_allAsm.write(rowNum, colNum, cellInfo, style=style_pending)
                    elif len(asmArray) == 0:
                        if colNum == 3:
                            ws_allAsm.write(rowNum, colNum, 'Not Done', style=style_noasm)
                        else:
                            ws_allAsm.write(rowNum, colNum, cellInfo, style=style_noasm)
                    else:
                        if colNum == 3:
                            ws_allAsm.write(rowNum, colNum, 'Not Done', style=style_normal)
                        else:
                            ws_allAsm.write(rowNum, colNum, cellInfo, style=style_normal)
                else:
                    if cellInfo in asmLogged:
                        ws_allAsm.write(rowNum, colNum, cellInfo, style=style_logged)
                    else:
                        ws_allAsm.write(rowNum, colNum, cellInfo, style=style_normal)
            rowNum += 1

            if tenantDomain in contentGLHCDomain:
                for colNum, cellInfo in enumerate(xlwtoutall.split(':')):
                    if colNum == 0:
                        ws_completeAsm.col(colNum).width = 256 * 57
                    else:
                        ws_completeAsm.col(colNum).width = 256 * 46
                    if colNum in {0, 1, 2}:
                        ws_completeAsm.write(completeNum, colNum, cellInfo, style=style_complete)
                    elif colNum == 3:
                        ws_completeAsm.write(completeNum, colNum, 'Done', style=style_complete)
                    else:
                        if cellInfo in asmLogged:
                            ws_completeAsm.write(completeNum, colNum, cellInfo, style=style_logged)
                        else:
                            ws_completeAsm.write(completeNum, colNum, cellInfo, style=style_normal)
                completeNum += 1

            if tenantDomain in contentPendingDomain:
                for colNum, cellInfo in enumerate(xlwtoutall.split(':')):
                    if colNum == 0:
                        ws_pendingAsm.col(colNum).width = 256 * 57
                    else:
                        ws_pendingAsm.col(colNum).width = 256 * 46
                    if colNum in {0, 1, 2}:
                        ws_pendingAsm.write(pendingNum, colNum, cellInfo, style=style_pending)
                    elif colNum == 3:
                        ws_pendingAsm.write(pendingNum, colNum, 'Pending', style=style_pending)
                    else:
                        if cellInfo in asmLogged:
                            ws_pendingAsm.write(pendingNum, colNum, cellInfo, style=style_logged)
                        else:
                            ws_pendingAsm.write(pendingNum, colNum, cellInfo, style=style_normal)
                pendingNum += 1

            if tenantDomain not in contentGLHCDomain and tenantDomain not in contentPendingDomain:
                for colNum, cellInfo in enumerate(xlwtoutall.split(':')):
                    if colNum == 0:
                        ws_notdoneAsm.col(colNum).width = 256 * 57
                    else:
                        ws_notdoneAsm.col(colNum).width = 256 * 46
                    if colNum in {0, 1, 2}:
                        if len(asmArray) == 0:
                            ws_notdoneAsm.write(notdoneNum, colNum, cellInfo, style=style_noasm)
                        else:
                            ws_notdoneAsm.write(notdoneNum, colNum, cellInfo, style=style_normal)
                    elif colNum == 3:
                        if len(asmArray) == 0:
                            ws_notdoneAsm.write(notdoneNum, colNum, 'Not Done', style=style_noasm)
                        else:
                            ws_notdoneAsm.write(notdoneNum, colNum, 'Not Done', style=style_normal)
                    else:
                        if cellInfo in asmLogged:
                            ws_notdoneAsm.write(notdoneNum, colNum, cellInfo, style=style_logged)
                        else:
                            ws_notdoneAsm.write(notdoneNum, colNum, cellInfo, style=style_normal)
                notdoneNum += 1

            if len(asmNotLogged) > 0:
                for colNum, cellInfo in enumerate(xlwtoutall.split(':')):
                    if colNum == 0:
                        ws_nonloggedAsm.col(colNum).width = 256 * 57
                    else:
                        ws_nonloggedAsm.col(colNum).width = 256 * 46
                    if colNum in {0, 1, 2}:
                        if tenantDomain in contentGLHCDomain:
                            ws_nonloggedAsm.write(nonloggedrowNum, colNum, cellInfo, style=style_complete)
                        elif tenantDomain in contentPendingDomain:
                            ws_nonloggedAsm.write(nonloggedrowNum, colNum, cellInfo, style=style_pending)
                        else:
                            ws_nonloggedAsm.write(nonloggedrowNum, colNum, cellInfo, style=style_normal)
                    elif colNum == 3:
                        if tenantDomain in contentGLHCDomain:
                            ws_nonloggedAsm.write(nonloggedrowNum, colNum, 'Done', style=style_complete)
                        elif tenantDomain in contentPendingDomain:
                            ws_nonloggedAsm.write(nonloggedrowNum, colNum, 'Pending', style=style_pending)
                        else:
                            ws_nonloggedAsm.write(nonloggedrowNum, colNum, 'Not Done', style=style_normal)
                    else:
                        if cellInfo in asmLogged:
                            ws_nonloggedAsm.write(nonloggedrowNum, colNum, cellInfo, style=style_logged)
                        else:
                            ws_nonloggedAsm.write(nonloggedrowNum, colNum, cellInfo, style=style_normal)
                nonloggedrowNum += 1

            xlwtoutallDone = xlwtout + ':Not Done' + asmArray
            if len(asmLogged) > 0 and len(asmNotLogged) == 0:
                for colNum, cellInfo in enumerate(xlwtoutallDone.split(':')):
                    if colNum == 0:
                        ws_loggedAsm.col(colNum).width = 256 * 57
                    else:
                        ws_loggedAsm.col(colNum).width = 256 * 46
                    if colNum in {0, 1, 2, 3}:
                        if tenantDomain in contentGLHCDomain:
                            if colNum == 3:
                                ws_loggedAsm.write(loggedrowNum, colNum, 'Done', style=style_complete)
                            else:
                                ws_loggedAsm.write(loggedrowNum, colNum, cellInfo, style=style_complete)
                        elif tenantDomain in contentPendingDomain:
                            if colNum == 3:
                                ws_loggedAsm.write(loggedrowNum, colNum, 'Pending', style=style_pending)
                            else:
                                ws_loggedAsm.write(loggedrowNum, colNum, cellInfo, style=style_pending)
                        else:
                            ws_loggedAsm.write(loggedrowNum, colNum, cellInfo, style=style_normal)
                    else:
                        if cellInfo in asmLogged:
                            ws_loggedAsm.write(loggedrowNum, colNum, cellInfo, style=style_logged)
                        else:
                            ws_loggedAsm.write(loggedrowNum, colNum, cellInfo, style=style_normal)
                loggedrowNum += 1

            if len(asmArray) == 0:
                for colNum, cellInfo in enumerate(xlwtoutall.split(':')):
                    if colNum == 0:
                        ws_noAsm.col(colNum).width = 256 * 57
                    else:
                        ws_noAsm.col(colNum).width = 256 * 46
                    if tenantDomain in contentGLHCDomain:
                        ws_noAsm.write(nonrowNum, colNum, cellInfo, style=style_complete)
                    elif tenantDomain in contentPendingDomain:
                        ws_noAsm.write(nonrowNum, colNum, cellInfo, style=style_pending)
                    else:
                        ws_noAsm.write(nonrowNum, colNum, cellInfo, style=style_noasm)
                nonrowNum += 1
    wb.save('GLC_Daily_Report.xls')


def getTenantsiWithLoggedAsm(singleorall):
    tenantList = []
    if singleorall == 'single':
        for row in range(1, SheetAsm.nrows):
            if SheetAsm.cell(row, ColumnASMEmail).value.strip() in contentAsm:
                tenantCaId = SheetAsm.cell(row, ColumnCaIdofASM).value.strip()
                for namerow in range(SheetCaOwner.nrows):
                    if tenantCaId == SheetCaOwner.cell(namerow, ColumnCaIdofCA).value.strip():
                        tenantName = SheetCaOwner.cell(namerow, ColumnTenantName).value.strip()
                        tenantList.append(tenantName)
    elif singleorall == 'all':
        for row in range(1, SheetCaOwner.nrows):
            tenantCaId = SheetCaOwner.cell(row, ColumnCaIdofCA).value.strip()
            logged = 1
            asmexists = 0
            for asmrow in range(SheetAsm.nrows):
                if tenantCaId == SheetAsm.cell(asmrow, ColumnCaIdofASM).value.strip() and includeAsm(
                        SheetAsm.cell(asmrow, ColumnASMEmail).value):
                    if SheetAsm.cell(asmrow, ColumnASMEmail).value.strip() not in contentAsm:
                        logged = 0
                    if re.match(r"[^@]+@[^@]+\.[^@]+", SheetAsm.cell(asmrow, ColumnASMEmail).value.strip()):
                        asmexists = 1
            if logged == 1 and asmexists == 1:
                tenantList.append(SheetCaOwner.cell(row, ColumnTenantName).value.strip())
    else:
        sys.exit(1)

    print(*sorted(list(set(tenantList))), sep="\n")


def getAllTenants(base_url, token, space_id='0c2209b5-da74-47b7-96f3-acdaeda0bd5f'):
    base_url = base_url.rstrip('/')
    req = requests.get(base_url + f'/api/iam/v1alpha2/tenants?spaceId={space_id}',
                       headers={'Authorization': f'Bearer {token}'})
    req.raise_for_status()
    return req.json()


def writeFile(users, GLHCDomains, PendingDomains):
    with open('allUsers.txt', 'w') as f:
        for user in users:
            f.write('{}\n'.format(user['userName']))
    f.close()
    with open('allGLHCDomains.txt', 'w') as f:
        for member in GLHCDomains['members']:
            if '@' in member['domainHint'] and 'caas' not in member['domainHint']:
                reglist = list(exrex.generate(member['domainHint']))
                for regitem in reglist:
                    f.write('{}\n'.format(regitem.split('@')[1]))
            else:
                f.write('{}\n'.format(member['domainHint']))
    f.close()
    with open('allPendingDomains.txt', 'w') as f:
        for member in PendingDomains['members']:
            if '@' in member['domainHint'] and 'caas' not in member['domainHint']:
                reglist = list(exrex.generate(member['domainHint']))
                for regitem in reglist:
                    f.write('{}\n'.format(regitem.split('@')[1]))
            else:
                f.write('{}\n'.format(member['domainHint']))
    f.close()


def getUsers(base_url, token, user_id=None, tenant_id='root'):
    base_url = base_url.rstrip('/')
    if not user_id:
        req = requests.get(base_url + '/api/iam/scim/v1/tenant/{}/Users'.format(tenant_id),
                           headers={'Authorization': 'Bearer {}'.format(token)})
    else:
        req = requests.get(base_url + f'/api/iam/scim/v1/tenant/{tenant_id}/Users?startIndex=2{user_id}',
                           headers={'Authorization': f'Bearer {token}'})
    req.raise_for_status()
    return req.json()


def getAllUsers(base_url, token, write_to_file=True, tenant_id='root'):
    base_url = base_url.rstrip('/')
    users = getUsers(base_url, token, tenant_id=tenant_id)
    all_users = users
    while len(users) >= 200:
        users = getUsers(base_url, token, users[-1]['id'], tenant_id=tenant_id)
        all_users.extend(users)
    if tenant_id == 'root':
        GLHCDomains = getAllTenants(base_url, token, space_id='9f70cc66-4613-47d3-ab28-a745587027b2')
        PendingDomains = getAllTenants(base_url, token, space_id='0c2209b5-da74-47b7-96f3-acdaeda0bd5f')
        if write_to_file:
            writeFile(all_users, GLHCDomains, PendingDomains)
    return all_users


def getUser(users, email, check_tenant=False):
    user = [user for user in users if user['userName'] == email]
    if len(user) == 1:
        return user[0]
    elif len(user) == 0:
        if check_tenant:
            return None
        raise ValueError(f'User {email} not logged into GLHC!')
    else:
        raise ValueError(f'Multiple records found for same email {email}!')


def getUserID(users, email):
    ids = [user['id'] for user in users if user['userName'] == email]
    if len(ids) == 1:
        return ids[0]

    else:
        raise ValueError('Multiple emails found!')


def provisionTenant(base_url, tenant, token):
    base_url = base_url.rstrip('/')
    country = input("Enter the country name: ")
    spaces = getAllSpaces(base_url, token_hpe)
    print(f'Fetching space ID for pending tenants...')
    space_id = [space['id'] for space in spaces['members'] if space['name'] == 'Pending Tenants'][0]
    print(f'Pending Tenants space ID: {space_id}')
    # TODO: Add check for integration using base_url
    print('Getting the users details...')
    glhc_users = getAllUsers(base_url, token, write_to_file=False)
    # If there is no Family Name in excel sheet, the script will fail
    contacts = [
        {"givenName": tenant.owner['name'].split()[0], "familyName": tenant.owner['name'].split(" ", 1)[-1].strip(),
         "email": tenant.owner['email'], "phoneNumber": "000-000-0000", "isOwner": True}]
    for email in tenant.asms:
        print('Fetching details for ASM {} from GLHC...'.format(email))
        asm = getUser(glhc_users, email)
        contacts.append(
            {"givenName": asm['name']['givenName'], "familyName": asm['name']['familyName'], "email": asm['userName'],
             "phoneNumber": "000-000-0000", "isOwner": True})
    data = {"name": tenant.name, "companyName": tenant.name, "country": country, "domainHint": tenant.domain,
            "lifecycle": "Active Trial",
            "contacts": deepcopy(contacts), "spaceId": space_id}
    print()
    pprint.pprint(data)
    print()
    confirm = input(
        "Please validate the above JSON snippet to be pushed for GLHC tenant "
        "creation (Press no to exit or any other key to continue): "
    )
    if confirm == "no":
        sys.exit()
    req = requests.post(base_url +
                        "/api/iam/v1alpha2/tenants",
                        headers={"Authorization": "Bearer " + token}, json=data)
    req.raise_for_status()
    return req.json()


def getTenantID(tenants, domain):
    for tenant in tenants["members"]:
        if tenant['domainHint'] == domain:
            return tenant['id']


def getTenantName(tenants, domain):
    for tenant in tenants["members"]:
        if tenant['domainHint'] == domain:
            return tenant['name']


def tenantDetails(base_url, tenant_id, token):
    base_url = base_url.rstrip('/')
    r = requests.get(base_url + "/api/iam/v1alpha2/tenants/{tenant_id}".format(tenant_id=tenant_id),
                     headers={"Authorization": "Bearer " + token})
    r.raise_for_status()
    return r.json()


def provisionASMs(base_url, tenant, token_hpe, token_spoke):
    base_url = base_url.rstrip('/')
    print('\nFetching ASM User IDs from GLHC...')
    glhc_users = getAllUsers(base_url, token_hpe, write_to_file=False)
    # tenant.asms = ['abhishek-s@hpe.com', 'adrian.lovell@hpe.com']
    if len(tenant.asms) == 0:
        print('Unable to find any ASMs to add to the tenant.')
        return
    for email in tenant.asms:
        print(f'Adding ASM {email} to the tenant {tenant.tenant_id}')
        if userExists(base_url, token_spoke, tenant.tenant_id, email):
            print("User already exists in the tenant, skipping!")
        else:
            user_id = getUserID(glhc_users, email)
            data = {"targetTenantId": f"{tenant.tenant_id}", "hpeGreenLakeRole": "member"}
            req = requests.post(base_url +
                                "/api/iam/scim/v1/extensions/tenant"
                                "/root/Users/{}/lifecycle/provision".format(user_id),
                                headers={"Authorization": "Bearer " + token_hpe}, json=data)
            req.raise_for_status()


def userExists(base_url, token, tenant_id, email):
    tenant_users = getAllUsers(base_url, token, write_to_file=False, tenant_id=tenant_id)
    user = getUser(tenant_users, email, check_tenant=True)
    return True if user and getUser(tenant_users, email, check_tenant=True)['userName'] == email else False


def provisionLocalUsers(base_url, tenant, token):
    base_url = base_url.rstrip('/')
    # tenant.users =[{'name': 'test user 1', 'email': 'hpe-test-user1@cnlopb.ca'},{'name': 'test user 2',
    #                 'email': 'hpe-test-user2@cnlopb.ca'}]
    for user in tenant.users:
        # NOTE: script will fail if family name doesn't exist
        data = {"displayName": user['name'], "active": False,
                "userName": user['email'], "name": {"givenName": user['name'].split()[0],
                                                    "familyName": user['name'].split(" ", 1)[1].strip()},
                "password": "",
                "meta": {"sendEmail": False, "changePassword": False}}

        print(f"Creating user {user['email']} in tenant {tenant.tenant_id}")
        if userExists(base_url, token, tenant.tenant_id, user['email']):
            print("User already exists in the tenant, skipping!")
        else:
            req = requests.post(base_url + f"/api/iam/scim/v1/tenant/{tenant.tenant_id}/Users",
                                headers={"Authorization": "Bearer " + token,
                                         'Content-type': 'application/scim+json', 'Accept': 'application/json'},
                                json=data)
            req.raise_for_status()
            if req.json()['active']:
                print("ERROR! User created in ACTIVE state but must be in STAGED state."
                      " Please delete it manually. Aborting user provisioning!")
                sys.exit(1)
    print(f"Creating GLHC Verifier user hpe-glhc-verifier@{tenant.domain}")
    if userExists(base_url, token, tenant.tenant_id, f'hpe-glhc-verifier@{tenant.domain}'):
        print("GLHC Verifier user already exists!")
    else:
        passwd = ""
        while passwd == "":
            passwd = input('Enter password for GLHC Verifier user: ')
            if passwd != "":
                break
            print("Password can't be empty!")
        data = {"displayName": 'GLHC Verifier', "active": True, "userName":
            f'hpe-glhc-verifier@{tenant.domain}',
                "name": {"givenName": 'GLHC', "familyName": 'Verifier'}, "password": passwd,
                "meta": {"sendEmail": False, "changePassword": False}}
        req = requests.post(base_url + "/api/iam/scim/v1/tenant/{}/Users".format(tenant.tenant_id),
                            headers={"Authorization": "Bearer " + token, 'Content-type': 'application/scim+json',
                                     'Accept': 'application/json'}, json=data)
        req.raise_for_status()
    print('All the users are successfully provisioned!\n')


def getAllRoles(base_url, token):
    req = requests.get(base_url + '/api/iam/v1alpha2/roles',
                       headers={"Authorization": "Bearer " + token})
    req.raise_for_status()
    return req.json()


def getAllGroups(base_url, token, tenant_id='root'):
    base_url = base_url.rstrip('/')
    groups = getGroups(base_url, token, tenant_id=tenant_id)
    all_groups = groups
    while len(groups) >= 200:
        groups = getGroups(base_url, token, groups[-1]['id'], tenant_id=tenant_id)
        all_groups.extend(groups)
    return all_groups


def getGroups(base_url, token, group_id=None, tenant_id='root'):
    if not group_id:
        req = requests.get(base_url + f'/api/iam/scim/v1/tenant/{tenant_id}/Groups',
                           headers={'Authorization': 'Bearer {}'.format(token)})
    else:
        req = requests.get(base_url + f'/api/iam/scim/v1/tenant/{tenant_id}/Groups?count=200&startIndex={group_id}',
                           headers={'Authorization': f'Bearer {token}'})
    req.raise_for_status()
    return req.json()['Resources']


def getAllSpaces(base_url, token):
    req = requests.get(base_url + '/api/iam/v1alpha2/spaces',
                       headers={"Authorization": "Bearer " + token})
    req.raise_for_status()
    return req.json()


def getAllAssignments(base_url, token):
    req = requests.get(base_url + '/api/iam/v1alpha2/assignments', headers={"Authorization": "Bearer " + token})
    req.raise_for_status()
    return req.json()


def assignmentExists(base_url, token, id, role_id, space_id):
    all_assignments = getAllAssignments(base_url, token)

    assignments = [assignment for assignment in all_assignments['members'] if
                   role_id == assignment['roleId'] and space_id == assignment['spaceId']]
    for assignment in assignments:
        if id in assignment['subjects']:
            return True
    return False


def provisionOwnerAssignments(base_url, tenant, token):
    base_url = base_url.rstrip('/')
    cx_team = ['junaid.ali@hpe.com', 'galal.hamid@hpe.com', 'nadja.sarsur@hpe.com',
               'cem.tan@hpe.com', 'srinadh-reddy.kotu@hpe.com', 'paul.stenson@hpe.com',
               'ciaran.otuathail@hpe.com']
    iam_team = ['ryan.brandt@hpe.com', 'jeff.green@hpe.com', 'travis.tripp@hpe.com',
                'craig.bryant@hpe.com', 'joe.keen@hpe.com']

    asms = tenant.asms
    owners_emails = iam_team + cx_team + asms
    tenant_users = getAllUsers(base_url, token, write_to_file=False, tenant_id=tenant.tenant_id)
    owners_with_ids = [{'email': user['userName'], 'id': user['id']} for user in tenant_users if
                       user['userName'] in owners_emails]

    all_roles = getAllRoles(base_url, token)
    all_spaces = getAllSpaces(base_url, token)

    # pprint.pprint(all_spaces)
    all_rss_space = [space['id'] for space in all_spaces['members'] if space['name'] == 'All Resources'][0]
    owner_role = [role['id'] for role in all_roles['members'] if role['name'] == 'IAM Owner'][0]

    print('Assigning IAM Owner permissions to CX, IAM and ASMs...')

    for user in owners_with_ids:
        if assignmentExists(base_url, token, f"users/{user['id']}", owner_role, all_rss_space):
            print(f"IAM Owner permission already exists for user {user['email']}")
        else:
            data = {"subjects": [f"users/{user['id']}"],
                    "roleId": owner_role,
                    "spaceId": all_rss_space}
            pprint.pprint(data)

            req = requests.post(base_url + '/api/iam/v1alpha2/assignments',
                                headers={"Authorization": "Bearer " + token}, json=data)
            req.raise_for_status()

    print(f"Successfully assigned owners to tenant {tenant.tenant_id}\n")


def provisionSpaces(base_url, tenant_id, token, space_name):
    data = {"name": space_name,
            "resources": [],
            "parentSpaceId": ""}

    all_spaces = getAllSpaces(base_url, token)
    all_rss_space = [space['id'] for space in all_spaces['members'] if space['name'] == 'All Resources'][0]
    data['parentSpaceId'] = all_rss_space

    if space_name not in [space['name'] for space in all_spaces['members']]:
        req = requests.post(base_url + '/api/iam/v1alpha2/spaces', headers={"Authorization": "Bearer " + token},
                            json=data)
        req.raise_for_status()
        print("Space {} successfully created in tenant {}".format(space_name, tenant_id))
    else:
        print("Space {} already exists in tenant {}".format(space_name, tenant_id))

    create_ca_client = input("Creating CA client resources, if CA resources are successfully "
                             "created before, press 'skip' to skip this step: ")
    if create_ca_client != 'skip':
        client_id = input("\nPlease create CA client in Okta and provide client ID: ")
        client_secret = input("Please provide client SECRET: ")
        all_spaces = getAllSpaces(base_url, token)
        space_id = [space['id'] for space in all_spaces['members'] if space['name'] == space_name][0]

        print("Assigning space the following permissions")
        print("Authorization Broker Contributor, Space Contributor, Role Contributor")
        all_roles = getAllRoles(base_url, token)
        roles = [role['id'] for role in all_roles['members'] if
                 role['name'] in ('Authorization Broker Contributor', 'Space Contributor', 'Role Contributor')]

        for role in roles:
            data = {"subjects":
                        ["clients/" + client_id], "roleId": role, "spaceId": space_id}
            if assignmentExists(base_url, token, f"clients/{client_id}", role, space_id):
                print(f"Role {role} already assigned to space {space_name}")
            else:
                pprint.pprint(data)
                req = requests.post(base_url + '/api/iam/v1alpha2/assignments',
                                    headers={"Authorization": "Bearer " + token}, json=data)
                req.raise_for_status()
                print(f'Successfully assigned role {role} to client {client_id} in space {space_name}')
        broker_ca = subprocess.call(['./broker_ca.sh', tenant_id, client_id, client_secret])
        if broker_ca == 0:
            print('Successfully added resources to _consumption-analytics space!\n')
        else:
            print('Failed adding resources to  _consumption-analytics space!')
            sys.exit(1)


def provisionRssInDefault(base_url, token, tenant):
    print("\nCreating resources and assignments in default space...")
    data = [
        {
            "op": "add",
            "path": "/resources/-",
            "value": {
                "id": "consumption-analytics",
                "name": "Consumption Analytics",
                "abId": "consumption-analytics"
            }
        }
    ]
    all_spaces = getAllSpaces(base_url, token)
    space_id = [space['id'] for space in all_spaces['members'] if space['name'] == 'Default'][0]
    req = requests.patch(base_url + '/api/iam/v1alpha2/spaces/' + space_id,
                         headers={"Accept": "application/vnd.hpe.v1+json",
                                  'cache-control': 'no-cache',
                                  'Content-Type': 'application/json',
                                  "Authorization": "Bearer " + token}, json=data)
    req.raise_for_status()

    all_roles = getAllRoles(base_url, token)
    all_spaces = getAllSpaces(base_url, token)
    all_users = getAllUsers(base_url, token, write_to_file=False, tenant_id=tenant.tenant_id)

    default_space = [space['id'] for space in all_spaces['members'] if space['name'] == 'Default'][0]
    ca_role = [role['id'] for role in all_roles['members'] if role['name'] == 'Consumption Analytics Contributor'][0]

    verifier_user = getUserID(all_users, f'hpe-glhc-verifier@{tenant.domain}')
    if not assignmentExists(base_url, token, f'users/{verifier_user}', ca_role, default_space):
        data = {"subjects": [f"users/{verifier_user}"],
                "roleId": ca_role,
                "spaceId": default_space}

        pprint.pprint(data)

        req = requests.post(base_url + '/api/iam/v1alpha2/assignments',
                            headers={"Authorization": "Bearer " + token}, json=data)
        req.raise_for_status()
    else:
        print(f'Assignment already exists for GLHC Verifier user!')


def getAllTenantsRss(base_url, token):
    req = requests.get(base_url + '/api/iam/v1alpha2/resources/tenant',
                       headers={"Authorization": "Bearer " + token})
    req.raise_for_status()
    return req.json()


def getSpaceID(all_spaces, space_name):
    space = [space['id'] for space in all_spaces['members'] if space['name'] == space_name]
    if len(space) > 1:
        raise Exception(f'Multiple spaces with the same name {space_name} found!')
    if len(space) == 0:
        raise Exception(f'Unable to find any space with name {space_name}!')
    return space[0]


def getSpaceResources(base_url, token, from_space_id):
    req = requests.get(base_url + f'/api/iam/v1alpha2/spaces/{from_space_id}?view=full',
                       headers={"Authorization": "Bearer " + token})
    req.raise_for_status()
    return req.json()['resources']


def getTenantRss(all_tenants, tenant_name):
    return [tenant for tenant in all_tenants['subPaths'] if tenant['name'] == tenant_name].pop(0)['resourceIdentifier']


def moveTenant(base_url, token, tenant_name, from_space, to_space):
    if from_space == to_space:
        raise Exception("Source and destination spaces must be different!")
    print('Fetching tenant and space details...')
    all_tenants_rss = getAllTenantsRss(base_url, token)
    spaces = getAllSpaces(base_url, token)
    from_space_id = getSpaceID(spaces, from_space)
    to_space_id = getSpaceID(spaces, to_space)
    glhc_tenants = getAllTenants(base_url, token, from_space_id)
    tenant = [tenant for tenant in glhc_tenants['members'] if tenant['name'] == tenant_name]
    if not tenant:
        print(f'Unable to find tenant in {from_space} space!')
        sys.exit(1)
    else:
        tenant = tenant.pop(0)

    print('Successfully fetched required details!')
    tenant_id = [tenant['id'] for tenant in glhc_tenants['members'] if tenant_name == tenant['name']].pop(0)

    from_space_rss = getSpaceResources(base_url, token, from_space_id)
    to_space_rss = getSpaceResources(base_url, token, to_space_id)
    to_tenant_rss = getTenantRss(all_tenants_rss, tenant_name)
    from_tenant_rss = [rss for rss in from_space_rss if rss['id'] == tenant_id].pop(0)

    print(f'Adding tenant {tenant_name} to space {to_space}')
    print(f"\nID: {tenant['id']:30} Name: {tenant['name']:30} Domain: {tenant['domainHint']}\n")

    if to_space == 'Pending Tenants':
        to_tenant_rss['name'] = ''
    if tenant_id in [rss['id'] for rss in to_space_rss]:
        print(f'Tenant {tenant_name} already exists in space {to_space}, skipping!')
    else:
        confirm = input('Press "yes" to confirm: ')
        if confirm != 'yes':
            print(f'Tenant {tenant_name} is not moved to {to_space}')
            sys.exit(1)
        to_space_rss.append(to_tenant_rss)
        data = [{'op': 'replace', 'path': '/name', 'value': f'{to_space}'},
                {'op': 'replace',
                 'path': '/resources',
                 'value': to_space_rss}]
        r = requests.patch(base_url + f'/api/iam/v1alpha2/spaces/{to_space_id}',
                           headers={'Authorization': 'Bearer ' + token}, json=data)
        r.raise_for_status()

    print(f'Removing tenant {tenant_name} - {tenant_id} from space {from_space}')
    to_space_rss = getSpaceResources(base_url, token, to_space_id)
    if tenant_id not in [rss['id'] for rss in from_space_rss]:
        print(f'Tenant {tenant_name} doesn\'t exist in space {from_space}, skipping!')
    else:
        confirm = input(f'Press "yes" to confirm (check from UI if tenant is available in {to_space} space before '
                        f'proceeding): ')
        if confirm != 'yes':
            print(f'Tenant {tenant_name} is not removed to {from_space}')
            sys.exit(1)
        if tenant_id not in [rss['id'] for rss in to_space_rss]:
            print(f'Unable to find tenant {tenant_name} in space {to_space}. Please add it to that space before '
                  f'removing it from {from_space}!')
            sys.exit(1)
        from_space_rss.remove(from_tenant_rss)
        data = [{'op': 'replace', 'path': '/name', 'value': f'{from_space}'},
                {'op': 'replace',
                 'path': '/resources',
                 'value': from_space_rss}]
        r = requests.patch(base_url + f'/api/iam/v1alpha2/spaces/{from_space_id}',
                           headers={'Authorization': 'Bearer ' + token}, json=data)
        r.raise_for_status()
    print(f'Tenant {tenant_name} is successfully moved from {from_space} to {to_space}!')


def getGroupUsers(base_url, token, tenant_id, group_id):
    base_url = base_url.rstrip('/')
    # TODO: Only fetches first 200 users
    r = requests.get(base_url + f'/api/iam/scim/v1/extensions/tenant/{tenant_id}/Groups/{group_id}/users',
                     headers={'Authorization': 'Bearer ' + token})
    r.raise_for_status()
    return r.json()['Resources']


def assignToGroups(base_url, token, tenant):
    base_url = base_url.rstrip('/')
    if tenant.name == 'HPE':
        print('Customer tenant must not be HPE root tenant!')
        sys.exit(1)
    all_groups = getAllGroups(base_url, token, tenant.tenant_id)
    all_users = getAllUsers(base_url, token, write_to_file=False, tenant_id=tenant.tenant_id)

    non_hpe_users = [{'email': user['userName'], 'id': user['id']} for user in all_users if
                     'hpe.com' not in user['userName']]
    non_hpe_group = 'GreenLake Central Default Contributors'
    non_hpe_group_id = [group['id'] for group in all_groups if group['displayName'] == non_hpe_group].pop(0)
    group_users = getGroupUsers(base_url, token, tenant.tenant_id, non_hpe_group_id)
    if not group_users:
        group_users = []
    else:
        group_users = [user['userName'] for user in group_users]

    print(f'Adding customer users to group {non_hpe_group}:')
    pprint.pprint(non_hpe_users)
    input('Press "Enter" to confirm: ')
    for user in non_hpe_users:
        if user['email'] in group_users:
            print(f"User {user['email']} already exists in GLC tenant {tenant.tenant_name} !")
        else:
            data = {"userID": f"{user['id']}"}
            r = requests.post(
                base_url + f'/api/iam/scim/v1/extensions/tenant/{tenant.tenant_id}/Groups/{non_hpe_group_id}/users',
                headers={'Authorization': 'Bearer ' + token}, json=data)
            r.raise_for_status()

    asms = tenant.asms
    asms_group = f'hpe-greenlake-account-service-manager-{tenant_id}'
    asm_group_id = [group['id'] for group in all_groups if group['displayName'] == asms_group].pop(0)
    asms_with_ids = [{'email': user['userName'], 'id': user['id']} for user in all_users if
                     user['userName'] in asms]
    asm_group_users = getGroupUsers(base_url, token, tenant.tenant_id, asm_group_id)
    if not asm_group_users:
        asm_group_users = []
    else:
        asm_group_users = [user['userName'] for user in asm_group_users]

    print(f'\nAdding ASMs to group {asms_group}:')
    pprint.pprint(asms_with_ids)
    input('Press "Enter" to confirm: ')
    for user in asms_with_ids:
        if user['email'] in asm_group_users:
            print(f"User {user['email']} already exists in GLC tenant {tenant.tenant_name} !")
        else:
            data = {"userID": f"{user['id']}"}
            r = requests.post(base_url + f"/api/iam/scim/v1/extensions/tenant/{tenant_id}/Groups/{asm_group_id}/users",
                              headers={'Authorization': 'Bearer ' + token}, json=data)
            r.raise_for_status()

    print('Removing direct user role assignments...')
    assignments = getAllAssignments(base_url, token)
    user_assignments = [assignment for assignment in assignments['members'] if 'users' in assignment['subjects'][0]]
    if len(user_assignments) < 1:
        print('No direct user assignments found!')
    else:
        pprint.pprint(user_assignments)
        for assignment in user_assignments:
            r = requests.delete(base_url + f'/api/iam/v1alpha2/assignments/{assignment["id"]}',
                                headers={'Authorization': 'Bearer ' + token})
            r.raise_for_status()
            print(f'Existing direct user assignment with id {assignment["id"]} deleted!')


if __name__ == "__main__":
    base_url = 'https://client.greenlake.hpe.com'
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--searchtenant", help="Search tenant in the list and show information")
    parser.add_argument("-T", "--findtenant", help="Find tenant in the list and show information")
    parser.add_argument("-n", "--searchasm", help="Search tenant in the list and show non-logged ASM information")
    parser.add_argument("-N", "--findasm", help="Find tenant in the list and show non-logged ASM information")
    parser.add_argument("-d", "--searchdomain", help="Search domain in the list and show tenant information")
    parser.add_argument("-D", "--finddomain", help="Find exact domain and show tenant information")
    parser.add_argument("-l", "--list", choices=['single', 'all'],
                        help="List the tenants if at least one or all ASM(s) logged in")
    parser.add_argument("-r", "--report", action="store_true", help="Generate complete report")
    parser.add_argument("-a", "--update", help="Update ASM and tenant information")
    parser.add_argument("-p", "--provision", help="Provision new tenant")
    parser.add_argument("-P", "--provision-rss", help="Provision tenant, users, add ASMs, spaces etc.")
    parser.add_argument("-m", "--move-tenant", help="Provide exact tenant name from GLC. "
                                                    "Moves that tenant from source space to destination space")
    parser.add_argument("--assign-to-groups", dest='assign_to_groups', default=False, action='store_true',
                        help="Assigns customer users and ASMs to proper groups")
    args = parser.parse_args()
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    if args.update:
        getAllUsers(base_url, args.update)

    if args.move_tenant:
        token_hpe = os.getenv("TOKEN_HPE")
        if not token_hpe:
            print("TOKEN_HPE not set!")
            token_hpe = input("Enter GLHC Authorization Token from HPE tenant (ensure you are getting token from "
                              "Pending Tenants space): ")
        moveTenant(base_url, token_hpe, args.move_tenant, 'Pending Tenants', 'GLHC Customers')
        sys.exit()

    if args.searchtenant or args.findtenant or args.searchasm or args.findasm or args.list or args.report or args.provision or args.provision_rss or args.finddomain or args.searchdomain:
        ColumnTenantName = 1
        ColumnCaIdofCA = 0
        ColumnCaIdofUL = 2
        ColumnCaIdofASM = 0
        ColumnCaIdofPortal = 1  ###
        ColumnCaIdofBilling = 0
        ColumnPortalOwner = 2
        ColumnPortalOwnerEmail = 3
        ColumnUserEmail = 0
        ColumnUserName = 1
        ColumnASMName = 1
        ColumnASMSurname = 2
        ColumnASMEmail = 3
        ColumnBilling = 1
        ColumnPortalId = 0  ###
        ColumnDomain = 5  #

        try:
            FileTenant = xlrd.open_workbook('tenant.xlsx')
            SheetCaOwner = FileTenant.sheet_by_name('CA Tenant and Owner')
            SheetUser = FileTenant.sheet_by_name('User List')
            SheetAsm = FileTenant.sheet_by_name('ASMs')
            SheetPortal = FileTenant.sheet_by_name('Portal IDs')  ###
            SheetBilling = FileTenant.sheet_by_name('No of Billing IDs in CA Tenant')
        except:
            print('Unable to open excel sheet tenant.xlsx')
            sys.exit(2)

        try:
            FileAsm = open("allUsers.txt", "r")
            FileGLHCDomain = open("allGLHCDomains.txt", "r")
            FilePendingDomain = open("allPendingDomains.txt", "r")
        except:
            print('Unable to open allUsers.txt. Did you run tenant.py -a <token>?')
            sys.exit(2)

        contentAsm = FileAsm.read()
        contentGLHCDomain = FileGLHCDomain.read()
        contentPendingDomain = FilePendingDomain.read()
        if args.report:
            getReport()
        elif args.findtenant:
            getTenantInfo(tenantName=args.findtenant, setexact='exact')
        elif args.searchtenant:
            getTenantInfo(tenantName=args.searchtenant)
        elif args.findasm:
            getTenantInfo(tenantName=args.findasm, notLogged='listit', setexact='exact')
        elif args.searchasm:
            getTenantInfo(tenantName=args.searchasm, notLogged='listit')
        elif args.finddomain:
            tenant = getDomain(tenantDomain=args.finddomain)
            if not tenant:
                print(f'Unable to find any tenant record in the sheet for the domain {args.finddomain}')
                sys.exit()
            token_hpe = os.getenv("TOKEN_HPE")
            if not token_hpe:
                print("TOKEN_HPE not set!")
                confirm = input("Press 'yes' to check GLHC Tenant ID and Name or 'Enter' to exit: ")
                if confirm == 'yes':
                    token_hpe = input("Enter GLHC Authorization Token from HPE tenant (ensure you are getting the token "
                                      "from Pending Tenants space): ")
                else:
                    sys.exit()
            print('Fetching GLHC tenant details from "GLHC Customers" space...')
            glhc_tenants = getAllTenants(base_url, token_hpe, space_id='9f70cc66-4613-47d3-ab28-a745587027b2')
            tenant_id = getTenantID(glhc_tenants, tenant.domain)
            tenant_name = getTenantName(glhc_tenants, tenant.domain)
            print(f"GLHC Tenant Name: {tenant_name}")
            print(f"GLHC Tenant ID  : {tenant_id}")
        elif args.searchdomain:
            getDomain(tenantDomain=args.searchdomain, searchIn=True)
        elif args.list:
            getTenantsiWithLoggedAsm(args.list)
        elif args.assign_to_groups:
            if not args.provision_rss:
                print('Please also provide -P flag with exact tenant name from the excel sheet')
                sys.exit(1)
            tenant = getTenantInfo(tenantName=args.provision_rss,
                                   setexact='exact')
            if not tenant:
                print("Please provide the exact tenant name to search for in the sheet.\nExiting!")
                sys.exit(1)
            token_hpe = os.getenv("TOKEN_HPE")
            if not token_hpe:
                print("TOKEN_HPE not set!")
                token_hpe = input("Enter GLHC Authorization Token from HPE tenant (ensure you are getting the token "
                                  "from Pending Tenants space): ")
            token_spoke = os.getenv("TOKEN_SPOKE")
            if not token_spoke:
                print("TOKEN_SPOKE not set!")
                token_spoke = input("Enter GLHC Authorization Token from Spoke/Customer tenant: ")
            glhc_tenants = getAllTenants(base_url, token_hpe, space_id='9f70cc66-4613-47d3-ab28-a745587027b2')
            tenant_id = getTenantID(glhc_tenants, tenant.domain)
            if tenant_id is None:
                raise ValueError('Unable to find the tenant Id with the domain {}'.format(tenant.domain))
            print('Fetching tenant details from GLHC...')
            details = tenantDetails(base_url, tenant_id, token_hpe)
            tenant.name = details['name']
            print(f"\nID: {details['id']:30} Name: {details['name']:30} Domain: {details['domainHint']}\n")
            tenant.tenant_id = details['id']
            assignToGroups(base_url, token_spoke, tenant)
            sys.exit()
        elif args.provision or args.provision_rss:
            token_hpe = os.getenv("TOKEN_HPE")
            if not token_hpe:
                print("TOKEN_HPE not set!")
                token_hpe = input("Enter GLHC Authorization Token from HPE tenant: ")
            tenant = getTenantInfo(tenantName=args.provision if args.provision else args.provision_rss,
                                   setexact='exact')
            if '@' in tenant.domain:
                tenant.domain = tenant.domain.split('@')[-1]
            # print(tenant)
            if args.provision:
                print('\n\n\n\n--------------------------------------------------------------')
                print(f'        Provisioning New Tenant')
                print('--------------------------------------------------------------')
                tenant.name = input("Enter new GLHC tenant name: ")
                print("New Tenant ID: " + provisionTenant(base_url, tenant, token_hpe)['id'])
                sys.exit(0)
            elif args.provision_rss:
                print('\n\n\n\n--------------------------------------------------------------')
                print(f'        Provisioning Resources in the new tenant')
                print('--------------------------------------------------------------')
                glhc_tenants = getAllTenants(base_url, token_hpe)
                token_spoke = os.getenv("TOKEN_SPOKE")
                if not token_spoke:
                    print("TOKEN_SPOKE not set!")
                    token_spoke = input("Enter GLHC Authorization Token from Customer tenant: ")
                tenant_id = getTenantID(glhc_tenants, tenant.domain)
                if tenant_id is None:
                    raise ValueError('Unable to find the tenant Id with the domain {}'.format(tenant.domain))
                print('Fetching tenant details from GLHC...')
                details = tenantDetails(base_url, tenant_id, token_hpe)
                tenant.name = details['name']
                print(f"\nID: {details['id']:30} Name: {details['name']:30} Domain: {details['domainHint']}\n")
                tenant.tenant_id = details['id']
                confirm = input("Run command (yes to provision resources in this tenant, anything else to exit)? ")
                if confirm == "yes":
                    # print("Tenant Record: {}".format(tenant))
                    print("\nThe following ASMs will be added to the tenant:")
                    pprint.pprint(tenant.asms)
                    print("\nThe following local users will be added to the tenant:")
                    pprint.pprint(tenant.users)
                    input('\nPress Enter to continue...')
                    provisionASMs(base_url, tenant, token_hpe, token_spoke)
                    provisionLocalUsers(base_url, tenant, token_spoke)
                    provisionOwnerAssignments(base_url, tenant, token_spoke)
                    provisionSpaces(base_url, tenant.tenant_id, token_spoke, '_consumption-analytics')
                    provisionRssInDefault(base_url, token_spoke, tenant)
        FileAsm.close()
        FileTenant.release_resources()
#else:
    #sys.exit(1)
