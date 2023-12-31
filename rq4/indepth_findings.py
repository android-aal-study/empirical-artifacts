import json
import os
import re
from itertools import product


result_sets = ['fdroid', 'gplay', 'malware']
apis = ['field', 'method']
types = ['', '-without-obfuscator']




def _to_lines(fn):
    return set(open(fn, encoding='utf8').read().strip().split('\n'))

def find_extra_cutomized_apis():
    non_aal = _to_lines('all-non-aal.txt')
    t = types[0]
    for r, a in product(result_sets, apis):
        fn0 = f'extra-{r}/extra-{r}-total-{a}{t}.txt'
        fn1 = f'extra-{r}/extra-{r}-androidx-or-support-{a}{t}.txt'
        total = _to_lines(fn0)
        sx = _to_lines(fn1)
        diff = total.difference(sx)
        is_covered = diff.intersection(non_aal)
        print((r, a, t), 'total', len(total), 'support/androidx', len(sx), 'non-aal', len(is_covered))
        if is_covered:
            with open(f'covered_non_aal/{r}-{a}-{t}.txt', 'w') as w:
                for line in sorted(is_covered):
                    w.write(line)
                    w.write('\n')



def _transform_extra(api):
    seg = api[1:-1].replace(":", "").split()
    return seg[0] + '->' + seg[2]

def backtrack_nonaal_apis():
    r = result_sets[1]
    used = set()
    fn = f'covered_non_aal/{r}-field-.txt'
    used.update(_to_lines(fn))
    fn = f'covered_non_aal/{r}-method-.txt'
    used.update(_to_lines(fn))
    for jf in os.listdir(f'{r}_result'):
        json_fn = f'{r}_result/{jf}'
        with open(json_fn) as j:
            items = json.load(j)['compassMethods']
        has_non_aal = False
        for item in items:
            extra_it = map(_transform_extra, item['call_external_APIs'])
            extras = list(extra_it)
            if used.intersection(extras):
                has_non_aal = True
                print(jf, item)
        if has_non_aal:
            print('-'*80)
"""
output of fdroid:
---
nya.miku.wishmaster_54.json {'method': '<nya.miku.wishmaster.lib.ClickableLinksTextView: void onStartTemporaryDetach()>', 'call_APIs': ['<android.view.View: boolean isFocused()>', '<android.view.View: void clearFocus()>'], 'call_external_APIs': ['<android.widget.TextView: void onStartTemporaryDetach()>'], 'call_reflect_APIs': []}
--------------------------------------------------------------------------------
io.github.muntashirakon.AppManager_423.json {'method': '<io.github.muntashirakon.AppManager.compat.AppOpsManagerCompat: boolean isMiuiOp(int)>', 'call_APIs': [], 'call_external_APIs': ['<android.app.AppOpsManager: int MIUI_OP_START>'], 'call_reflect_APIs': []}
io.github.muntashirakon.AppManager_423.json {'method': '<io.github.muntashirakon.AppManager.compat.AppOpsManagerCompat: java.util.List getAllOps()>', 'call_APIs': [], 'call_external_APIs': ['<android.app.AppOpsManager: int MIUI_OP_END>', '<android.app.AppOpsManager: int MIUI_OP_START>'], 'call_reflect_APIs': []}
--------------------------------------------------------------------------------
================================================================================================================================================================================================================================================================================================================================
output of gplay:    
---
com.runtastic.android.json {'method': '<com.samsung.android.sdk.bt.gatt.BluetoothGatt: boolean isBLEDevice(android.bluetooth.BluetoothDevice)>', 'call_APIs': [], 'call_external_APIs': ['<android.bluetooth.BluetoothDevice: int getDeviceType()>'], 'call_reflect_APIs': []}
com.runtastic.android.json {'method': '<com.samsung.android.sdk.bt.gatt.BluetoothGattServer: boolean isBLEDevice(android.bluetooth.BluetoothDevice)>', 'call_APIs': [], 'call_external_APIs': ['<android.bluetooth.BluetoothDevice: int getDeviceType()>'], 'call_reflect_APIs': []}
--------------------------------------------------------------------------------
com.vmware.view.client.android.json {'method': '<c.c.a.a.d.d: void <init>()>', 'call_APIs': ['<android.util.Log: int d(java.lang.String,java.lang.String)>', '<android.os.Build$VERSION: int SDK_INT>'], 'call_external_APIs': ['<android.os.Build$VERSION: int SEM_INT>'], 'call_reflect_APIs': []}
com.vmware.view.client.android.json {'method': '<c.c.a.a.d.b: void <init>(android.content.Context)>', 'call_APIs': ['<android.util.Log: int d(java.lang.String,java.lang.String)>', '<android.os.Build$VERSION: int SDK_INT>', '<android.content.Context: java.lang.Object getSystemService(java.lang.String)>'], 'call_external_APIs': ['<android.os.Build$VERSION: int SEM_INT>'], 'call_reflect_APIs': []}
--------------------------------------------------------------------------------
kr.co.aladin.elibrary.json {'method': '<com.samsung.android.authfw.pass.sdk.authenticator.FingerprintManager$SemFingerprintOperation: void authenticate(int,android.os.CancellationSignal,com.samsung.android.authfw.pass.sdk.authenticator.FingerprintManager$FingerprintAuthenticateListener)>', 'call_APIs': [], 'call_external_APIs': ['<android.os.UserHandle: int semGetMyUserId()>'], 'call_reflect_APIs': []}
--------------------------------------------------------------------------------
com.sec.android.app.shealth.json {'method': '<com.samsung.android.app.shealth.j0.c.g: int c(android.content.Context)>', 'call_APIs': [], 'call_external_APIs': ['<android.os.Build$VERSION: int SEM_INT>'], 'call_reflect_APIs': []}
com.sec.android.app.shealth.json {'method': '<com.samsung.android.app.shealth.j0.b.p.b: void setAnchor(android.app.Dialog,android.view.View,int)>', 'call_APIs': [], 'call_external_APIs': ['<android.app.Dialog: void semSetAnchor(android.view.View,int)>'], 'call_reflect_APIs': []}
com.sec.android.app.shealth.json {'method': '<com.samsung.android.app.shealth.j0.b.c: boolean isDesktopDockConnected(android.content.Context)>', 'call_APIs': ['<android.content.Context: android.content.Intent registerReceiver(android.content.BroadcastReceiver,android.content.IntentFilter)>', '<android.content.Intent: int getIntExtra(java.lang.String,int)>', '<android.content.IntentFilter: void <init>(java.lang.String)>'], 'call_external_APIs': ['<android.os.Build$VERSION: int SEM_PLATFORM_INT>'], 'call_reflect_APIs': []}
com.sec.android.app.shealth.json {'method': '<com.samsung.android.app.shealth.j0.b.p.a: android.app.ActivityOptions setPopOverOptions(android.app.ActivityOptions,int[],int[],android.graphics.Point[],int[])>', 'call_APIs': [], 'call_external_APIs': ['<android.app.ActivityOptions: android.app.ActivityOptions semSetPopOverOptions(int[],int[],android.graphics.Point[],int[])>', '<android.os.Build$VERSION: int SEM_PLATFORM_INT>'], 'call_reflect_APIs': []}
com.sec.android.app.shealth.json {'method': '<com.samsung.android.app.shealth.j0.b.p.g: void setRoundedCorners(android.view.View,int)>', 'call_APIs': [], 'call_external_APIs': ['<android.view.View: void semSetRoundedCorners(int)>', '<android.os.Build$VERSION: int SEM_INT>'], 'call_reflect_APIs': []}
com.sec.android.app.shealth.json {'method': '<com.samsung.android.app.shealth.j0.b.p.c: void setType(android.view.View,int)>', 'call_APIs': [], 'call_external_APIs': ['<android.view.View: void semSetHoverPopupType(int)>'], 'call_reflect_APIs': []}
com.sec.android.app.shealth.json {'method': '<com.samsung.android.app.shealth.j0.b.l: boolean isCovered(android.content.res.Configuration)>', 'call_APIs': [], 'call_external_APIs': ['<android.content.res.Configuration: int semMobileKeyboardCovered>'], 'call_reflect_APIs': []}
com.sec.android.app.shealth.json {'method': '<com.samsung.android.app.shealth.j0.c.g: int b(android.content.Context)>', 'call_APIs': [], 'call_external_APIs': ['<android.os.Build$VERSION: int SEM_PLATFORM_INT>'], 'call_reflect_APIs': []}
com.sec.android.app.shealth.json {'method': '<com.samsung.android.app.shealth.j0.b.a: boolean removeBond(android.bluetooth.BluetoothDevice)>', 'call_APIs': [], 'call_external_APIs': ['<android.bluetooth.BluetoothDevice: boolean semRemoveBond()>'], 'call_reflect_APIs': []}
com.sec.android.app.shealth.json {'method': '<com.samsung.android.app.shealth.j0.b.c: boolean isDesktopMode(android.content.Context)>', 'call_APIs': ['<android.content.res.Resources: android.content.res.Configuration getConfiguration()>', '<android.content.Context: android.content.res.Resources getResources()>'], 'call_external_APIs': ['<android.content.res.Configuration: int semDesktopModeEnabled>', '<android.os.Build$VERSION: int SEM_PLATFORM_INT>'], 'call_reflect_APIs': []}
com.sec.android.app.shealth.json {'method': '<com.samsung.android.app.shealth.j0.b.i: void a(android.content.Intent,int,boolean)>', 'call_APIs': [], 'call_external_APIs': ['<android.content.Intent: void semSetLaunchOverTargetTask(int,boolean)>'], 'call_reflect_APIs': []}
com.sec.android.app.shealth.json {'method': '<com.samsung.android.app.shealth.j0.b.o.m: com.samsung.android.app.shealth.j0.b.o.l getWritableDatabase(byte[])>', 'call_APIs': [], 'call_external_APIs': ['<android.database.sqlite.SQLiteCantOpenDatabaseException: boolean semIsWrongPasswordException()>'], 'call_reflect_APIs': []}
com.sec.android.app.shealth.json {'method': '<com.samsung.android.app.shealth.j0.b.a: java.lang.String getAliasName(android.bluetooth.BluetoothDevice)>', 'call_APIs': [], 'call_external_APIs': ['<android.bluetooth.BluetoothDevice: java.lang.String semGetAliasName()>'], 'call_reflect_APIs': []}
com.sec.android.app.shealth.json {'method': '<com.samsung.android.app.shealth.j0.c.g: int a(android.content.Context)>', 'call_APIs': [], 'call_external_APIs': ['<android.os.Build$VERSION: int SEM_FIRST_SDK_INT>'], 'call_reflect_APIs': []}
com.sec.android.app.shealth.json {'method': '<com.samsung.android.app.shealth.j0.b.o.j: void onCorruption(android.database.sqlite.SQLiteDatabase)>', 'call_APIs': ['<android.database.sqlite.SQLiteDatabase: java.lang.String getPath()>'], 'call_external_APIs': ['<android.database.sqlite.SQLiteDatabase: boolean semIsDatabaseCorrupted()>'], 'call_reflect_APIs': []}
com.sec.android.app.shealth.json {'method': '<com.samsung.android.app.shealth.j0.b.e: boolean checkSepVersion(android.content.Context)>', 'call_APIs': [], 'call_external_APIs': ['<android.os.Build$VERSION: int SEM_PLATFORM_INT>'], 'call_reflect_APIs': []}
com.sec.android.app.shealth.json {'method': '<com.samsung.android.app.shealth.j0.b.h: boolean isAccessoryKeyboard(android.content.Context)>', 'call_APIs': ['<android.content.Context: java.lang.Object getSystemService(java.lang.String)>'], 'call_external_APIs': ['<android.view.inputmethod.InputMethodManager: boolean semIsAccessoryKeyboard()>'], 'call_reflect_APIs': []}
com.sec.android.app.shealth.json {'method': '<com.samsung.android.app.shealth.j0.b.p.e: void setGoToTopEnabled(android.widget.AbsListView,boolean,boolean)>', 'call_APIs': ['<android.view.View: android.content.Context getContext()>', '<android.content.res.Resources: android.content.res.Configuration getConfiguration()>', '<android.content.res.Configuration: int uiMode>', '<android.content.Context: android.content.res.Resources getResources()>'], 'call_external_APIs': ['<android.widget.AbsListView: void semSetGoToTopEnabled(boolean)>', '<android.widget.AbsListView: void semSetGoToTopEnabled(boolean,int)>'], 'call_reflect_APIs': []}
com.sec.android.app.shealth.json {'method': '<com.samsung.android.app.shealth.j0.b.p.b: void setAnchor(android.app.Dialog,android.view.View)>', 'call_APIs': [], 'call_external_APIs': ['<android.app.Dialog: void semSetAnchor(android.view.View)>'], 'call_reflect_APIs': []}
com.sec.android.app.shealth.json {'method': '<com.samsung.android.app.shealth.j0.b.a: boolean createBond(android.bluetooth.BluetoothDevice)>', 'call_APIs': ['<android.bluetooth.BluetoothDevice: boolean createBond()>'], 'call_external_APIs': ['<android.bluetooth.BluetoothDevice: boolean semCreateBond(byte)>'], 'call_reflect_APIs': []}
com.sec.android.app.shealth.json {'method': '<com.samsung.android.app.shealth.j0.b.p.c: com.samsung.android.app.shealth.runtime.contract.ui.SamsungHoverPopupWindow getWindow(android.view.View)>', 'call_APIs': [], 'call_external_APIs': ['<android.view.View: com.samsung.android.widget.SemHoverPopupWindow semGetHoverPopup(boolean)>'], 'call_reflect_APIs': []}
com.sec.android.app.shealth.json {'method': '<com.samsung.android.app.shealth.j0.b.e: boolean isScreenSharing(android.content.Context)>', 'call_APIs': ['<android.content.Context: java.lang.Object getSystemService(java.lang.String)>'], 'call_external_APIs': ['<android.hardware.display.DisplayManager: int semCheckScreenSharingSupported()>'], 'call_reflect_APIs': []}
com.sec.android.app.shealth.json {'method': '<com.samsung.android.app.shealth.j0.b.o.m: com.samsung.android.app.shealth.j0.b.o.l getReadableDatabase(byte[])>', 'call_APIs': [], 'call_external_APIs': ['<android.database.sqlite.SQLiteCantOpenDatabaseException: boolean semIsWrongPasswordException()>'], 'call_reflect_APIs': []}
com.sec.android.app.shealth.json {'method': '<com.samsung.android.app.shealth.j0.b.n: char[] a(android.text.TextPaint,java.lang.String,char[])>', 'call_APIs': [], 'call_external_APIs': ['<android.text.TextUtils: char[] semGetPrefixCharForSpan(android.text.TextPaint,java.lang.CharSequence,char[])>'], 'call_reflect_APIs': []}
com.sec.android.app.shealth.json {'method': '<com.samsung.android.app.shealth.j0.b.f: boolean isShipVersion()>', 'call_APIs': [], 'call_external_APIs': ['<android.os.Debug: boolean semIsProductDev()>'], 'call_reflect_APIs': []}
com.sec.android.app.shealth.json {'method': '<com.samsung.android.sdk.cover.ScoverManager: void setCoverModeToWindow(android.view.Window,int)>', 'call_APIs': ['<android.util.Log: int w(java.lang.String,java.lang.String)>', '<android.view.Window: void setAttributes(android.view.WindowManager$LayoutParams)>', '<android.view.Window: android.view.WindowManager$LayoutParams getAttributes()>'], 'call_external_APIs': ['<android.view.WindowManager$LayoutParams: int coverMode>'], 'call_reflect_APIs': []}
com.sec.android.app.shealth.json {'method': '<com.samsung.android.app.shealth.j0.b.p.a: android.app.ActivityOptions setChooserPopOverOptions(android.app.ActivityOptions,int)>', 'call_APIs': [], 'call_external_APIs': ['<android.app.ActivityOptions: android.app.ActivityOptions semSetChooserPopOverPosition(int)>', '<android.os.Build$VERSION: int SEM_PLATFORM_INT>'], 'call_reflect_APIs': []}
com.sec.android.app.shealth.json {'method': '<com.samsung.android.app.shealth.j0.b.h: void forceHideSoftInput(android.view.inputmethod.InputMethodManager)>', 'call_APIs': [], 'call_external_APIs': ['<android.view.inputmethod.InputMethodManager: boolean semForceHideSoftInput()>'], 'call_reflect_APIs': []}
com.sec.android.app.shealth.json {'method': '<d.f.a.d.a.c.d: void <clinit>()>', 'call_APIs': ['<android.text.TextUtils: boolean isEmpty(java.lang.CharSequence)>'], 'call_external_APIs': ['<android.os.SemSystemProperties: java.lang.String get(java.lang.String,java.lang.String)>', '<android.os.Debug: boolean semIsProductDev()>'], 'call_reflect_APIs': []}
com.sec.android.app.shealth.json {'method': '<com.samsung.android.app.shealth.j0.b.e: void setMediaPlayerParameter(android.media.MediaPlayer)>', 'call_APIs': [], 'call_external_APIs': ['<android.media.MediaPlayer: boolean semSetParameter(int,int)>'], 'call_reflect_APIs': []}
com.sec.android.app.shealth.json {'method': '<com.samsung.android.app.shealth.j0.b.p.g: void setRoundedCorners(android.view.View,int,int)>', 'call_APIs': ['<android.graphics.Color: int parseColor(java.lang.String)>'], 'call_external_APIs': ['<android.view.View: int semGetRoundedCorners()>', '<android.view.View: void semSetRoundedCorners(int)>', '<android.view.View: void semSetRoundedCornerColor(int,int)>', '<android.os.Build$VERSION: int SEM_INT>'], 'call_reflect_APIs': []}
com.sec.android.app.shealth.json {'method': '<com.samsung.android.app.shealth.j0.b.p.f: void setMultiSelectionEnabled(android.widget.TextView,boolean)>', 'call_APIs': [], 'call_external_APIs': ['<android.widget.TextView: void semSetMultiSelectionEnabled(boolean)>'], 'call_reflect_APIs': []}
com.sec.android.app.shealth.json {'method': '<com.samsung.android.app.shealth.j0.b.j: void setPendingIntentAfterUnlock(android.content.Context,android.app.PendingIntent,android.content.Intent)>', 'call_APIs': ['<android.util.Log: int i(java.lang.String,java.lang.String)>', '<android.content.Context: java.lang.Object getSystemService(java.lang.String)>'], 'call_external_APIs': ['<android.app.KeyguardManager: void semSetPendingIntentAfterUnlock(android.app.PendingIntent,android.content.Intent)>'], 'call_reflect_APIs': []}
com.sec.android.app.shealth.json {'method': '<com.samsung.android.app.shealth.j0.b.p.b: void setAnchor(android.app.Dialog,int,int)>', 'call_APIs': [], 'call_external_APIs': ['<android.app.Dialog: void semSetAnchor(int,int)>'], 'call_reflect_APIs': []}
--------------------------------------------------------------------------------
com.lovense.wear.json {'method': '<com.samsung.android.sdk.bt.gatt.BluetoothGatt: boolean isBLEDevice(android.bluetooth.BluetoothDevice)>', 'call_APIs': [], 'call_external_APIs': ['<android.bluetooth.BluetoothDevice: int getDeviceType()>'], 'call_reflect_APIs': []}
com.lovense.wear.json {'method': '<com.samsung.android.sdk.bt.gatt.BluetoothGattServer: boolean isBLEDevice(android.bluetooth.BluetoothDevice)>', 'call_APIs': [], 'call_external_APIs': ['<android.bluetooth.BluetoothDevice: int getDeviceType()>'], 'call_reflect_APIs': []}
--------------------------------------------------------------------------------
com.citrix.Receiver.json {'method': '<rd.d: void <init>()>', 'call_APIs': ['<android.util.Log: int d(java.lang.String,java.lang.String)>', '<android.os.Build$VERSION: int SDK_INT>'], 'call_external_APIs': ['<android.os.Build$VERSION: int SEM_INT>'], 'call_reflect_APIs': []}
com.citrix.Receiver.json {'method': '<rd.b: void <init>(android.content.Context)>', 'call_APIs': ['<android.util.Log: int d(java.lang.String,java.lang.String)>', '<android.os.Build$VERSION: int SDK_INT>', '<android.content.Context: java.lang.Object getSystemService(java.lang.String)>'], 'call_external_APIs': ['<android.os.Build$VERSION: int SEM_INT>'], 'call_reflect_APIs': []}
--------------------------------------------------------------------------------
com.fambase.venus.json {'method': '<com.samsung.android.sdk.bt.gatt.BluetoothGatt: boolean isBLEDevice(android.bluetooth.BluetoothDevice)>', 'call_APIs': [], 'call_external_APIs': ['<android.bluetooth.BluetoothDevice: int getDeviceType()>'], 'call_reflect_APIs': []}
com.fambase.venus.json {'method': '<com.samsung.android.sdk.bt.gatt.BluetoothGattServer: boolean isBLEDevice(android.bluetooth.BluetoothDevice)>', 'call_APIs': [], 'call_external_APIs': ['<android.bluetooth.BluetoothDevice: int getDeviceType()>'], 'call_reflect_APIs': []}
--------------------------------------------------------------------------------
com.sec.android.app.sbrowser.json {'method': '<com.samsung.android.authfw.pass.sdk.authenticator.FingerprintManager$SemFingerprintOperation: void authenticate(int,android.os.CancellationSignal,com.samsung.android.authfw.pass.sdk.authenticator.FingerprintManager$FingerprintAuthenticateListener)>', 'call_APIs': [], 'call_external_APIs': ['<android.os.UserHandle: int semGetMyUserId()>'], 'call_reflect_APIs': []}
com.sec.android.app.sbrowser.json {'method': '<u7.v$a: void run()>', 'call_APIs': ['<android.os.Vibrator: void vibrate(android.os.VibrationEffect)>'], 'call_external_APIs': ['<android.view.HapticFeedbackConstants: int semGetVibrationIndex(int)>', '<android.os.VibrationEffect$SemMagnitudeType: android.os.VibrationEffect$SemMagnitudeType TYPE_TOUCH>', '<android.os.VibrationEffect: android.os.VibrationEffect semCreateWaveform(int,int,android.os.VibrationEffect$SemMagnitudeType)>'], 'call_reflect_APIs': []}
com.sec.android.app.sbrowser.json {'method': '<com.samsung.android.sdk.cover.ScoverManager: void setCoverModeToWindow(android.view.Window,int)>', 'call_APIs': ['<android.util.Log: int w(java.lang.String,java.lang.String)>', '<android.view.Window: void setAttributes(android.view.WindowManager$LayoutParams)>', '<android.view.Window: android.view.WindowManager$LayoutParams getAttributes()>'], 'call_external_APIs': ['<android.view.WindowManager$LayoutParams: int coverMode>'], 'call_reflect_APIs': []}
--------------------------------------------------------------------------------
com.mi.android.globallauncher.json {'method': '<com.miui.launcher.utils.PortableUtilsInRom: java.lang.String getCurrentWallpaperInfo(android.content.Context,java.lang.String)>', 'call_APIs': ['<android.content.ContentResolver: android.database.Cursor query(android.net.Uri,java.lang.String[],java.lang.String,java.lang.String[],java.lang.String)>', '<android.database.Cursor: void close()>', '<android.net.Uri: android.net.Uri parse(java.lang.String)>', '<android.database.Cursor: java.lang.String getString(int)>', '<android.content.Context: android.content.Context createPackageContextAsUser(java.lang.String,int,android.os.UserHandle)>', '<android.database.Cursor: boolean moveToFirst()>', '<android.os.Build$VERSION: int SDK_INT>', '<android.content.Context: java.lang.String getPackageName()>', '<android.os.UserHandle: android.os.UserHandle OWNER>'], 'call_external_APIs': ['<android.content.Context: android.content.ContentResolver getContentResolverForUser(android.os.UserHandle)>'], 'call_reflect_APIs': []}
com.mi.android.globallauncher.json {'method': '<com.miui.launcher.utils.MiuiWindowManagerUtils: void setExtraFlag(android.view.Window,int,int)>', 'call_APIs': [], 'call_external_APIs': ['<android.view.Window: void setExtraFlags(int,int)>'], 'call_reflect_APIs': []}
com.mi.android.globallauncher.json {'method': '<com.miui.launcher.utils.MiuiWindowManagerUtils: void changeStatusBarMode(android.view.Window,boolean)>', 'call_APIs': ['<android.view.Window: android.view.View getDecorView()>', '<android.view.View: int getSystemUiVisibility()>', '<android.view.View: void setSystemUiVisibility(int)>', '<android.view.Window: void setAttributes(android.view.WindowManager$LayoutParams)>', '<android.os.Build$VERSION: int SDK_INT>', '<android.view.Window: android.view.WindowManager$LayoutParams getAttributes()>'], 'call_external_APIs': ['<android.view.WindowManager$LayoutParams: int extraFlags>'], 'call_reflect_APIs': []}
com.mi.android.globallauncher.json {'method': '<com.miui.launcher.utils.ActivityUtilsCompat: android.app.ActivityOptions makeClipRevealAnimation(android.view.View,int,int,int,int,boolean)>', 'call_APIs': [], 'call_external_APIs': ['<android.app.ActivityOptions: android.app.ActivityOptions makeClipRevealAnimation(android.view.View,int,int,int,int,boolean)>'], 'call_reflect_APIs': []}
com.mi.android.globallauncher.json {'method': '<com.miui.launcher.utils.PortableUtilsInRom: void updateCurrentWallpaperInfo(android.content.Context,java.lang.String,java.lang.String)>', 'call_APIs': ['<android.net.Uri: android.net.Uri parse(java.lang.String)>', '<android.content.Context: android.content.Context createPackageContextAsUser(java.lang.String,int,android.os.UserHandle)>', '<android.content.ContentValues: void put(java.lang.String,java.lang.String)>', '<android.content.ContentResolver: int update(android.net.Uri,android.content.ContentValues,java.lang.String,java.lang.String[])>', '<android.os.Build$VERSION: int SDK_INT>', '<android.content.Context: java.lang.String getPackageName()>', '<android.os.UserHandle: android.os.UserHandle OWNER>', '<android.content.ContentValues: void <init>()>'], 'call_external_APIs': ['<android.content.Context: android.content.ContentResolver getContentResolverForUser(android.os.UserHandle)>'], 'call_reflect_APIs': []}
com.mi.android.globallauncher.json {'method': '<com.miui.launcher.utils.LauncherUtils: java.lang.String getSender(android.content.Intent)>', 'call_APIs': [], 'call_external_APIs': ['<android.content.Intent: java.lang.String getSender()>'], 'call_reflect_APIs': []}
--------------------------------------------------------------------------------
com.sec.penup.json {'method': '<com.samsung.android.spen.libse.SeView: com.samsung.android.spen.libinterface.HoverPopupWindowInterface getHoverPopupWindow()>', 'call_APIs': [], 'call_external_APIs': ['<android.view.View: com.samsung.android.widget.SemHoverPopupWindow semGetHoverPopup(boolean)>'], 'call_reflect_APIs': []}
com.sec.penup.json {'method': '<com.samsung.android.spen.libse.SeInputMethodManager: boolean isAccessoryKeyboardState()>', 'call_APIs': [], 'call_external_APIs': ['<android.view.inputmethod.InputMethodManager: boolean semIsAccessoryKeyboard()>'], 'call_reflect_APIs': []}
com.sec.penup.json {'method': '<com.samsung.android.spen.libse.SeView: boolean isSupportDcHaptic()>', 'call_APIs': ['<android.view.View: android.content.Context getContext()>', '<android.content.Context: java.lang.Object getSystemService(java.lang.String)>'], 'call_external_APIs': ['<android.os.Vibrator: int semGetSupportedVibrationType()>'], 'call_reflect_APIs': []}
com.sec.penup.json {'method': '<com.samsung.android.spen.libse.SeInputMethodManager: boolean isInputMethodShown()>', 'call_APIs': [], 'call_external_APIs': ['<android.view.inputmethod.InputMethodManager: boolean semIsInputMethodShown()>'], 'call_reflect_APIs': []}
com.sec.penup.json {'method': '<com.samsung.android.spen.libse.SeView: void setPointerIcon(android.content.Context,int)>', 'call_APIs': ['<android.view.PointerIcon: android.view.PointerIcon getSystemIcon(android.content.Context,int)>', '<android.os.Build$VERSION: int SDK_INT>'], 'call_external_APIs': ['<android.view.View: void semSetPointerIcon(int,android.view.PointerIcon)>'], 'call_reflect_APIs': []}
com.sec.penup.json {'method': '<com.sec.penup.ui.main.MainBaseActivity: void x1()>', 'call_APIs': ['<android.media.AudioAttributes$Builder: android.media.AudioAttributes$Builder setContentType(int)>', '<android.media.AudioAttributes$Builder: android.media.AudioAttributes$Builder setFlags(int)>', '<android.media.AudioAttributes$Builder: android.media.AudioAttributes build()>', '<android.content.ContextWrapper: android.content.Context getApplicationContext()>', '<android.media.AudioAttributes$Builder: android.media.AudioAttributes$Builder setUsage(int)>', '<android.media.AudioAttributes$Builder: void <init>()>', '<android.os.Vibrator: void vibrate(android.os.VibrationEffect,android.media.AudioAttributes)>', '<android.content.Context: java.lang.Object getSystemService(java.lang.String)>'], 'call_external_APIs': ['<android.view.HapticFeedbackConstants: int semGetVibrationIndex(int)>', '<android.os.VibrationEffect$SemMagnitudeType: android.os.VibrationEffect$SemMagnitudeType TYPE_TOUCH>', '<android.os.VibrationEffect: android.os.VibrationEffect semCreateWaveform(int,int,android.os.VibrationEffect$SemMagnitudeType)>'], 'call_reflect_APIs': []}
com.sec.penup.json {'method': '<com.samsung.android.spen.libse.SePointerIcon: void setHoveringSpenIcon(android.content.Context,android.view.View,int,int)>', 'call_APIs': ['<android.view.PointerIcon: android.view.PointerIcon getSystemIcon(android.content.Context,int)>'], 'call_external_APIs': ['<android.view.View: void semSetPointerIcon(int,android.view.PointerIcon)>'], 'call_reflect_APIs': []}
com.sec.penup.json {'method': '<com.samsung.android.spen.libse.SePackageManager: int getSystemFeatureLevel(java.lang.String)>', 'call_APIs': [], 'call_external_APIs': ['<android.content.pm.PackageManager: int semGetSystemFeatureLevel(java.lang.String)>'], 'call_reflect_APIs': []}
com.sec.penup.json {'method': '<com.samsung.android.spen.libse.SeView: void performDCHapticFeedback(android.os.Vibrator)>', 'call_APIs': ['<android.view.View: android.content.Context getContext()>', '<android.content.Context: android.content.ContentResolver getContentResolver()>', '<android.provider.Settings$System: int getInt(android.content.ContentResolver,java.lang.String,int)>', '<android.os.Vibrator: void vibrate(android.os.VibrationEffect)>', '<android.os.Build$VERSION: int SDK_INT>'], 'call_external_APIs': ['<android.view.HapticFeedbackConstants: int semGetVibrationIndex(int)>', '<android.os.VibrationEffect$SemMagnitudeType: android.os.VibrationEffect$SemMagnitudeType TYPE_TOUCH>', '<android.os.VibrationEffect: android.os.VibrationEffect semCreateWaveform(int,int,android.os.VibrationEffect$SemMagnitudeType)>'], 'call_reflect_APIs': []}
com.sec.penup.json {'method': '<com.samsung.android.spen.libse.SeView: void setPointerIcon(android.content.res.Resources,android.graphics.Bitmap,float,float)>', 'call_APIs': ['<android.view.PointerIcon: android.view.PointerIcon create(android.graphics.Bitmap,float,float)>', '<android.os.Build$VERSION: int SDK_INT>'], 'call_external_APIs': ['<android.view.View: void semSetPointerIcon(int,android.view.PointerIcon)>'], 'call_reflect_APIs': []}
com.sec.penup.json {'method': '<com.samsung.android.spen.libse.SePointerIcon: void setHoveringSpenIcon(android.view.View,android.graphics.drawable.Drawable,android.graphics.Point)>', 'call_APIs': ['<android.graphics.Point: int x>', '<android.graphics.Point: int y>', '<android.view.PointerIcon: android.view.PointerIcon create(android.graphics.Bitmap,float,float)>'], 'call_external_APIs': ['<android.view.View: void semSetPointerIcon(int,android.view.PointerIcon)>'], 'call_reflect_APIs': []}
com.sec.penup.json {'method': '<com.samsung.android.sdk.pen.setting.util.SpenSettingUtilSIP: boolean isSIPShowing(android.view.inputmethod.InputMethodManager)>', 'call_APIs': [], 'call_external_APIs': ['<android.view.inputmethod.InputMethodManager: boolean semIsInputMethodShown()>'], 'call_reflect_APIs': []}
com.sec.penup.json {'method': '<com.samsung.android.spen.libse.SeView: void setHoverPopupType(int)>', 'call_APIs': [], 'call_external_APIs': ['<android.view.View: void semSetHoverPopupType(int)>'], 'call_reflect_APIs': []}
com.sec.penup.json {'method': '<com.samsung.android.spen.libse.SeView: void setPointerIcon(int,android.view.PointerIcon)>', 'call_APIs': [], 'call_external_APIs': ['<android.view.View: void semSetPointerIcon(int,android.view.PointerIcon)>'], 'call_reflect_APIs': []}
com.sec.penup.json {'method': '<com.samsung.android.sdk.pen.setting.util.SpenSettingUtilSIP: boolean forceHideSoftInput(android.content.Context,android.view.View)>', 'call_APIs': ['<android.content.Context: java.lang.Object getSystemService(java.lang.String)>'], 'call_external_APIs': ['<android.view.inputmethod.InputMethodManager: boolean semForceHideSoftInput()>'], 'call_reflect_APIs': []}
com.sec.penup.json {'method': '<com.samsung.android.spen.libse.SeMediaRecorder: void setDurationInterval(int)>', 'call_APIs': [], 'call_external_APIs': ['<android.media.MediaRecorder: void semSetDurationInterval(int)>'], 'call_reflect_APIs': []}
com.sec.penup.json {'method': '<com.sec.penup.ui.drawing.SpenBaseLayoutInitializeActivity: void e0(android.content.res.Configuration,android.content.res.Configuration)>', 'call_APIs': ['<android.content.res.Configuration: int screenHeightDp>', '<android.content.res.Configuration: int screenWidthDp>', '<android.app.Activity: void recreate()>'], 'call_external_APIs': ['<android.content.res.Configuration: int semDesktopModeEnabled>'], 'call_reflect_APIs': []}
com.sec.penup.json {'method': '<com.samsung.android.spen.libse.SePointerIcon: void setHoveringSpenIcon(android.view.View,android.graphics.drawable.Drawable,android.graphics.Point,int)>', 'call_APIs': ['<android.graphics.Point: int x>', '<android.graphics.Point: int y>', '<android.view.PointerIcon: android.view.PointerIcon create(android.graphics.Bitmap,float,float)>'], 'call_external_APIs': ['<android.view.View: void semSetPointerIcon(int,android.view.PointerIcon)>'], 'call_reflect_APIs': []}
com.sec.penup.json {'method': '<com.samsung.android.spen.libse.SeDesktopModeManager: boolean isDesktopMode()>', 'call_APIs': ['<android.content.res.Resources: android.content.res.Configuration getConfiguration()>', '<android.os.Build$VERSION: int SDK_INT>', '<android.content.Context: android.content.res.Resources getResources()>'], 'call_external_APIs': ['<android.content.res.Configuration: int semDesktopModeEnabled>'], 'call_reflect_APIs': []}
com.sec.penup.json {'method': '<com.samsung.android.spen.libse.SeSettingsSystem: int getIntForUser(android.content.ContentResolver,java.lang.String,int,int)>', 'call_APIs': [], 'call_external_APIs': ['<android.provider.Settings$System: int semGetIntForUser(android.content.ContentResolver,java.lang.String,int,int)>'], 'call_reflect_APIs': []}
com.sec.penup.json {'method': '<com.samsung.android.spen.libse.SeTypeface: java.lang.String getFontPathOfCurrentFontStyle(android.content.Context,int)>', 'call_APIs': ['<android.util.Log: int e(java.lang.String,java.lang.String)>'], 'call_external_APIs': ['<android.graphics.Typeface: java.lang.String semGetFontPathOfCurrentFontStyle(android.content.Context,int)>'], 'call_reflect_APIs': []}
com.sec.penup.json {'method': '<com.samsung.android.spen.libse.SeView: void performHapticFeedback(int)>', 'call_APIs': ['<android.view.View: boolean performHapticFeedback(int,int)>', '<android.view.View: android.content.Context getContext()>', '<android.view.View: boolean performHapticFeedback(int)>', '<android.content.Context: java.lang.Object getSystemService(java.lang.String)>'], 'call_external_APIs': ['<android.view.HapticFeedbackConstants: int semGetVibrationIndex(int)>', '<android.os.Vibrator: int semGetNumberOfSupportedPatterns()>', '<android.os.Build$VERSION: int SEM_INT>'], 'call_reflect_APIs': []}
com.sec.penup.json {'method': '<com.sec.penup.common.tools.k: boolean B(android.content.res.Configuration)>', 'call_APIs': [], 'call_external_APIs': ['<android.content.res.Configuration: int semDisplayDeviceType>'], 'call_reflect_APIs': []}
com.sec.penup.json {'method': '<com.samsung.android.spen.libse.SePointerIcon: void setHoveringSpenIcon(android.content.Context,android.view.View,int)>', 'call_APIs': ['<android.view.PointerIcon: android.view.PointerIcon getSystemIcon(android.content.Context,int)>'], 'call_external_APIs': ['<android.view.View: void semSetPointerIcon(int,android.view.PointerIcon)>'], 'call_reflect_APIs': []}
--------------------------------------------------------------------------------
com.weo.beeto.json {'method': '<com.samsung.android.sdk.camera.delegator.AbstractSemCamera: int getSepPlatformVersion(android.content.Context)>', 'call_APIs': [], 'call_external_APIs': ['<android.os.Build$VERSION: int SEM_PLATFORM_INT>'], 'call_reflect_APIs': []}
--------------------------------------------------------------------------------
com.samsung.accessory.json {'method': '<com.sec.android.diagmonagent.dma.aperf.utils.aPerfValidation: boolean morePalette()>', 'call_APIs': [], 'call_external_APIs': ['<android.os.Build$VERSION: int SEM_PLATFORM_INT>'], 'call_reflect_APIs': []}
com.samsung.accessory.json {'method': '<com.sec.android.diagmonagent.log.provider.utils.DiagMonUtil: boolean underPalette()>', 'call_APIs': [], 'call_external_APIs': ['<android.os.Build$VERSION: int SEM_PLATFORM_INT>'], 'call_reflect_APIs': []}
--------------------------------------------------------------------------------
com.samsung.android.app.watchmanager.json {'method': '<com.samsung.android.app.watchmanager.selibrary.BluetoothHeadsetManager: boolean disconnect(android.bluetooth.BluetoothHeadset,android.bluetooth.BluetoothDevice)>', 'call_APIs': [], 'call_external_APIs': ['<android.bluetooth.BluetoothHeadset: boolean semDisconnect(android.bluetooth.BluetoothDevice)>'], 'call_reflect_APIs': []}
com.samsung.android.app.watchmanager.json {'method': '<com.samsung.android.app.watchmanager.selibrary.BluetoothHeadsetManager: boolean connect(android.bluetooth.BluetoothHeadset,android.bluetooth.BluetoothDevice)>', 'call_APIs': [], 'call_external_APIs': ['<android.bluetooth.BluetoothHeadset: boolean semConnect(android.bluetooth.BluetoothDevice)>'], 'call_reflect_APIs': []}
com.samsung.android.app.watchmanager.json {'method': '<com.samsung.android.app.watchmanager.selibrary.BluetoothDeviceManager: byte[] getManufacturerData(android.bluetooth.BluetoothDevice)>', 'call_APIs': [], 'call_external_APIs': ['<android.bluetooth.BluetoothDevice: byte[] semGetManufacturerData()>'], 'call_reflect_APIs': []}
com.samsung.android.app.watchmanager.json {'method': '<com.samsung.android.app.twatchmanager.util.SafeRemoveTaskHandler: void start(android.app.Activity)>', 'call_APIs': ['<android.content.res.Resources: android.content.res.Configuration getConfiguration()>', '<android.view.ContextThemeWrapper: android.content.res.Resources getResources()>'], 'call_external_APIs': ['<android.content.res.Configuration: int semDesktopModeEnabled>'], 'call_reflect_APIs': []}
com.samsung.android.app.watchmanager.json {'method': '<com.samsung.android.app.watchmanager.selibrary.BluetoothDeviceManager: boolean createBond(android.bluetooth.BluetoothDevice)>', 'call_APIs': [], 'call_external_APIs': ['<android.bluetooth.BluetoothDevice: boolean semCreateBond(byte)>'], 'call_reflect_APIs': []}
com.samsung.android.app.watchmanager.json {'method': '<com.samsung.android.app.watchmanager.selibrary.BluetoothDeviceManager: boolean removeBond(android.bluetooth.BluetoothDevice)>', 'call_APIs': [], 'call_external_APIs': ['<android.bluetooth.BluetoothDevice: boolean semRemoveBond()>'], 'call_reflect_APIs': []}
com.samsung.android.app.watchmanager.json {'method': '<com.samsung.android.app.watchmanager.selibrary.BluetoothDeviceManager: java.lang.String getAliasName(android.bluetooth.BluetoothDevice)>', 'call_APIs': [], 'call_external_APIs': ['<android.bluetooth.BluetoothDevice: java.lang.String semGetAliasName()>'], 'call_reflect_APIs': []}
com.samsung.android.app.watchmanager.json {'method': '<com.samsung.android.app.twatchmanager.connectionmanager.scanner.BluetoothLEScanner: android.bluetooth.le.ScanSettings getScanSetting()>', 'call_APIs': ['<android.bluetooth.le.ScanSettings$Builder: android.bluetooth.le.ScanSettings$Builder setScanMode(int)>', '<android.bluetooth.le.ScanSettings$Builder: void <init>()>', '<android.bluetooth.le.ScanSettings$Builder: android.bluetooth.le.ScanSettings build()>'], 'call_external_APIs': ['<android.bluetooth.le.ScanSettings$Builder: android.bluetooth.le.ScanSettings$Builder semSetCustomScanParams(int,int)>'], 'call_reflect_APIs': []}
--------------------------------------------------------------------------------
com.innocaption.vpdp.json {'method': '<com.samsung.android.sdk.look.cocktailbar.SepCocktailBarManager: void setOnLongClickPendingIntentTemplate(android.widget.RemoteViews,int,android.app.PendingIntent)>', 'call_APIs': ['<android.os.Build$VERSION: int SDK_INT>'], 'call_external_APIs': ['<android.widget.RemoteViews: void semSetOnLongClickPendingIntentTemplate(int,android.app.PendingIntent)>'], 'call_reflect_APIs': []}
com.innocaption.vpdp.json {'method': '<com.samsung.android.sdk.look.cocktailbar.SdlCocktailBarManager: void setOnLongClickPendingIntent(android.widget.RemoteViews,int,android.app.PendingIntent)>', 'call_APIs': ['<android.os.Build$VERSION: int SDK_INT>'], 'call_external_APIs': ['<android.widget.RemoteViews: void semSetOnLongClickPendingIntent(int,android.app.PendingIntent)>'], 'call_reflect_APIs': []}
com.innocaption.vpdp.json {'method': '<com.samsung.android.sdk.look.cocktailbar.SepCocktailBarManager: void setOnLongClickPendingIntent(android.widget.RemoteViews,int,android.app.PendingIntent)>', 'call_APIs': ['<android.os.Build$VERSION: int SDK_INT>'], 'call_external_APIs': ['<android.widget.RemoteViews: void semSetOnLongClickPendingIntent(int,android.app.PendingIntent)>'], 'call_reflect_APIs': []}
com.innocaption.vpdp.json {'method': '<com.samsung.android.sdk.look.cocktailbar.SdlCocktailBarManager: void setOnLongClickPendingIntentTemplate(android.widget.RemoteViews,int,android.app.PendingIntent)>', 'call_APIs': ['<android.os.Build$VERSION: int SDK_INT>'], 'call_external_APIs': ['<android.widget.RemoteViews: void semSetOnLongClickPendingIntentTemplate(int,android.app.PendingIntent)>'], 'call_reflect_APIs': []}
--------------------------------------------------------------------------------
com.sec.android.easyMover.json {'method': '<r6.b: int i0()>', 'call_APIs': ['<android.util.Log: int e(java.lang.String,java.lang.String)>'], 'call_external_APIs': ['<android.os.Build$VERSION: int SEM_INT>'], 'call_reflect_APIs': []}
com.sec.android.easyMover.json {'method': '<com.sec.android.easyMover.ui.VersionActivity$c$a: void n()>', 'call_APIs': ['<android.widget.TextView: void setText(java.lang.CharSequence)>', '<android.widget.ProgressBar: void setMax(int)>', '<android.widget.ProgressBar: void setProgress(int)>', '<android.widget.ProgressBar: void setIndeterminate(boolean)>', '<android.content.Context: java.lang.String getString(int,java.lang.Object[])>', '<android.view.View: void setVisibility(int)>', '<android.app.Dialog: android.view.View findViewById(int)>'], 'call_external_APIs': ['<android.widget.ProgressBar: void semSetMode(int)>'], 'call_reflect_APIs': []}
com.sec.android.easyMover.json {'method': '<r6.b: void B(android.content.Context,int)>', 'call_APIs': ['<android.util.Log: int e(java.lang.String,java.lang.String,java.lang.Throwable)>', '<android.util.Log: int e(java.lang.String,java.lang.String)>', '<android.content.Context: java.lang.Object getSystemService(java.lang.String)>'], 'call_external_APIs': ['<android.hardware.usb.UsbManager: void semSetMode(int)>'], 'call_reflect_APIs': []}
com.sec.android.easyMover.json {'method': '<r6.b: boolean n(android.content.pm.PackageManager,long,q6.a$c)>', 'call_APIs': ['<android.util.Log: int e(java.lang.String,java.lang.String,java.lang.Throwable)>', '<android.util.Log: int e(java.lang.String,java.lang.String)>'], 'call_external_APIs': ['<android.content.pm.PackageManager: void semFreeStorageAndNotify(long,android.content.pm.PackageManager$SemFreeStorageNotifyListener)>'], 'call_reflect_APIs': []}
com.sec.android.easyMover.json {'method': '<r6.b: boolean C(android.content.Context)>', 'call_APIs': ['<android.util.Log: int d(java.lang.String,java.lang.String)>', '<android.util.Log: int e(java.lang.String,java.lang.String,java.lang.Throwable)>', '<android.os.Build$VERSION: int SDK_INT>', '<android.util.Log: int e(java.lang.String,java.lang.String)>', '<android.content.Context: java.lang.Object getSystemService(java.lang.String)>'], 'call_external_APIs': ['<android.os.UserManager: boolean semIsManagedProfile()>'], 'call_reflect_APIs': []}
com.sec.android.easyMover.json {'method': '<r6.b: int j0(android.content.Context)>', 'call_APIs': ['<android.util.Log: int d(java.lang.String,java.lang.String)>', '<android.util.Log: int e(java.lang.String,java.lang.String,java.lang.Throwable)>', '<android.util.Log: int e(java.lang.String,java.lang.String)>'], 'call_external_APIs': ['<android.os.UserHandle: int semGetMyUserId()>'], 'call_reflect_APIs': []}
com.sec.android.easyMover.json {'method': '<com.sec.android.easyMover.wireless.ble.d: void o(int,byte[],byte[])>', 'call_APIs': ['<android.os.Handler: void removeMessages(int)>', '<android.bluetooth.le.ScanFilter: byte[] getManufacturerData()>', '<android.bluetooth.le.ScanSettings$Builder: void <init>()>', '<android.bluetooth.le.ScanSettings$Builder: android.bluetooth.le.ScanSettings build()>', '<android.os.Handler: boolean sendEmptyMessage(int)>', '<android.os.Handler: boolean sendEmptyMessageDelayed(int,long)>', '<android.bluetooth.le.ScanSettings$Builder: android.bluetooth.le.ScanSettings$Builder setScanMode(int)>', '<android.bluetooth.le.ScanFilter$Builder: android.bluetooth.le.ScanFilter$Builder setManufacturerData(int,byte[],byte[])>', '<android.bluetooth.le.ScanFilter$Builder: android.bluetooth.le.ScanFilter build()>', '<android.os.Build$VERSION: int SDK_INT>', '<android.bluetooth.le.ScanFilter$Builder: void <init>()>'], 'call_external_APIs': ['<android.bluetooth.le.ScanSettings$Builder: android.bluetooth.le.ScanSettings$Builder semSetCustomScanParams(int,int)>'], 'call_reflect_APIs': []}
com.sec.android.easyMover.json {'method': '<r6.b: android.os.UserHandle e0(int)>', 'call_APIs': ['<android.util.Log: int e(java.lang.String,java.lang.String,java.lang.Throwable)>', '<android.util.Log: int e(java.lang.String,java.lang.String)>'], 'call_external_APIs': ['<android.os.UserHandle: android.os.UserHandle semOf(int)>'], 'call_reflect_APIs': []}
com.sec.android.easyMover.json {'method': '<r6.b: int U(android.content.Context)>', 'call_APIs': ['<android.util.Log: int e(java.lang.String,java.lang.String,java.lang.Throwable)>', '<android.util.Log: int e(java.lang.String,java.lang.String)>', '<android.content.Context: java.lang.Object getSystemService(java.lang.String)>'], 'call_external_APIs': ['<android.hardware.usb.UsbManager: int semGetPowerRoleStatus()>'], 'call_reflect_APIs': []}
com.sec.android.easyMover.json {'method': '<j2.c: boolean i()>', 'call_APIs': ['<android.content.Context: android.content.Context getApplicationContext()>', '<android.content.Context: boolean bindService(android.content.Intent,android.content.ServiceConnection,int)>', '<android.content.Intent: void <init>(android.content.Context,java.lang.Class)>', '<android.content.Intent: android.content.Intent putExtra(java.lang.String,java.io.Serializable)>', '<android.content.Intent: android.content.Intent putExtra(java.lang.String,boolean)>'], 'call_external_APIs': ['<android.content.Context: boolean semBindServiceAsUser(android.content.Intent,android.content.ServiceConnection,int,android.os.UserHandle)>', '<android.os.UserHandle: int semGetIdentifier()>', '<android.os.UserHandle: int semGetMyUserId()>'], 'call_reflect_APIs': []}
com.sec.android.easyMover.json {'method': '<r6.b: boolean u(android.content.Context)>', 'call_APIs': ['<android.util.Log: int i(java.lang.String,java.lang.String)>', '<android.util.Log: int e(java.lang.String,java.lang.String,java.lang.Throwable)>', '<android.os.Build$VERSION: int SDK_INT>', '<android.content.Context: java.lang.Object getSystemService(java.lang.String)>'], 'call_external_APIs': ['<android.os.UserManager: android.content.pm.SemUserInfo semGetSemUserInfo(int)>', '<android.content.pm.SemUserInfo: boolean isSecondNumberMode()>'], 'call_reflect_APIs': []}
com.sec.android.easyMover.json {'method': '<j2.k: j2.c u0()>', 'call_APIs': ['<android.os.SystemClock: long elapsedRealtime()>'], 'call_external_APIs': ['<android.os.UserHandle: int semGetIdentifier()>'], 'call_reflect_APIs': []}
com.sec.android.easyMover.json {'method': '<r6.b: boolean x(android.app.backup.BackupManager,android.os.ParcelFileDescriptor,java.lang.String)>', 'call_APIs': ['<android.util.Log: int e(java.lang.String,java.lang.String,java.lang.Throwable)>', '<android.util.Log: int e(java.lang.String,java.lang.String)>'], 'call_external_APIs': ['<android.app.backup.BackupManager: void semRestorePackage(android.os.ParcelFileDescriptor,java.lang.String)>'], 'call_reflect_APIs': []}
com.sec.android.easyMover.json {'method': '<t6.a: void a()>', 'call_APIs': ['<android.util.Log: int i(java.lang.String,java.lang.String)>', '<android.util.Log: int e(java.lang.String,java.lang.String)>'], 'call_external_APIs': ['<android.os.Build$VERSION: int SEM_INT>', '<android.os.Build$VERSION: int SEM_PLATFORM_INT>'], 'call_reflect_APIs': []}
com.sec.android.easyMover.json {'method': '<s7.l: boolean c(android.content.Context,java.lang.String,int)>', 'call_APIs': [], 'call_external_APIs': ['<android.os.UserHandle: int semGetMyUserId()>'], 'call_reflect_APIs': []}
com.sec.android.easyMover.json {'method': '<r6.b: boolean t(android.content.Context)>', 'call_APIs': ['<android.util.Log: int e(java.lang.String,java.lang.String,java.lang.Throwable)>', '<android.content.Context: android.content.res.Resources getResources()>', '<android.util.Log: int d(java.lang.String,java.lang.String)>', '<android.content.Context: java.lang.Object getSystemService(java.lang.Class)>', '<android.content.res.Resources: android.content.res.Configuration getConfiguration()>', '<android.os.Build$VERSION: int SDK_INT>', '<android.util.Log: int e(java.lang.String,java.lang.String)>', '<android.content.Context: java.lang.Object getSystemService(java.lang.String)>'], 'call_external_APIs': ['<android.content.res.Configuration: int semDesktopModeEnabled>'], 'call_reflect_APIs': []}
com.sec.android.easyMover.json {'method': '<r6.b: boolean c(android.app.backup.BackupManager,android.os.ParcelFileDescriptor,java.lang.String[],java.lang.String,int)>', 'call_APIs': ['<android.util.Log: int e(java.lang.String,java.lang.String,java.lang.Throwable)>', '<android.util.Log: int e(java.lang.String,java.lang.String)>'], 'call_external_APIs': ['<android.app.backup.BackupManager: java.util.Map semBackupPackage(android.os.ParcelFileDescriptor,java.lang.String[],java.lang.String,int)>'], 'call_reflect_APIs': []}
com.sec.android.easyMover.json {'method': '<l8.a: int o(l8.a$d,android.content.pm.PackageManager)>', 'call_APIs': ['<android.content.pm.PackageManager: android.content.pm.PackageInstaller getPackageInstaller()>', '<android.content.pm.PackageInstaller$SessionParams: void setInstallReason(int)>', '<android.graphics.BitmapFactory: android.graphics.Bitmap decodeFile(java.lang.String)>', '<android.content.pm.PackageInstaller: int createSession(android.content.pm.PackageInstaller$SessionParams)>', '<android.os.SystemClock: long elapsedRealtime()>', '<android.content.pm.PackageInstaller$SessionParams: void setAppPackageName(java.lang.String)>', '<android.content.pm.PackageInstaller$SessionParams: void <init>(int)>', '<android.content.pm.PackageInstaller$SessionParams: void setInstallLocation(int)>', '<android.os.Build$VERSION: int SDK_INT>', '<android.content.pm.PackageInstaller$SessionParams: void setAppLabel(java.lang.CharSequence)>', '<android.content.pm.PackageInstaller$SessionParams: void setAppIcon(android.graphics.Bitmap)>'], 'call_external_APIs': ['<android.content.pm.PackageInstaller$SessionParams: void semSetInstallFlagsSkipDexOptimization()>'], 'call_reflect_APIs': ['Landroid/content/pm/PackageInstaller$SessionParams;->setInstallerPackageName']}
com.sec.android.easyMover.json {'method': '<r6.b: void G(android.content.pm.PackageManager,java.lang.String,java.lang.String,android.os.UserHandle)>', 'call_APIs': ['<android.util.Log: int e(java.lang.String,java.lang.String,java.lang.Throwable)>', '<android.util.Log: int e(java.lang.String,java.lang.String)>'], 'call_external_APIs': ['<android.content.pm.PackageManager: void semGrantRuntimePermission(java.lang.String,java.lang.String,android.os.UserHandle)>'], 'call_reflect_APIs': []}
com.sec.android.easyMover.json {'method': '<s7.l: boolean d(android.content.Context,java.lang.String)>', 'call_APIs': [], 'call_external_APIs': ['<android.os.UserHandle: int semGetMyUserId()>'], 'call_reflect_APIs': []}
com.sec.android.easyMover.json {'method': '<r6.b: void Y(android.view.View,boolean)>', 'call_APIs': ['<android.util.Log: int e(java.lang.String,java.lang.String,java.lang.Throwable)>', '<android.util.Log: int e(java.lang.String,java.lang.String)>'], 'call_external_APIs': ['<android.view.View: void semSetHoverPopupType(int)>'], 'call_reflect_APIs': []}
com.sec.android.easyMover.json {'method': '<r6.b: void b0(android.bluetooth.BluetoothAdapter,boolean)>', 'call_APIs': ['<android.util.Log: int e(java.lang.String,java.lang.String,java.lang.Throwable)>', '<android.util.Log: int e(java.lang.String,java.lang.String)>'], 'call_external_APIs': ['<android.bluetooth.BluetoothAdapter: boolean semSetStandAloneBleMode(boolean)>'], 'call_reflect_APIs': []}
com.sec.android.easyMover.json {'method': '<r6.b: java.lang.String a(android.os.storage.StorageVolume)>', 'call_APIs': ['<android.util.Log: int e(java.lang.String,java.lang.String,java.lang.Throwable)>', '<android.util.Log: int e(java.lang.String,java.lang.String)>'], 'call_external_APIs': ['<android.os.storage.StorageVolume: java.lang.String semGetSubSystem()>'], 'call_reflect_APIs': []}
com.sec.android.easyMover.json {'method': '<j2.c: int C()>', 'call_APIs': [], 'call_external_APIs': ['<android.os.UserHandle: int semGetIdentifier()>'], 'call_reflect_APIs': []}
com.sec.android.easyMover.json {'method': '<s7.l: int a(android.content.Context)>', 'call_APIs': [], 'call_external_APIs': ['<android.os.UserHandle: int semGetMyUserId()>'], 'call_reflect_APIs': []}
com.sec.android.easyMover.json {'method': '<r6.b: int z(android.content.pm.PackageManager,java.lang.String,java.lang.String,android.os.UserHandle)>', 'call_APIs': ['<android.util.Log: int e(java.lang.String,java.lang.String,java.lang.Throwable)>', '<android.util.Log: int e(java.lang.String,java.lang.String)>'], 'call_external_APIs': ['<android.content.pm.PackageManager: int semGetPermissionFlags(java.lang.String,java.lang.String,android.os.UserHandle)>'], 'call_reflect_APIs': []}
com.sec.android.easyMover.json {'method': '<r6.b: java.lang.String P(android.os.storage.StorageVolume)>', 'call_APIs': ['<android.util.Log: int e(java.lang.String,java.lang.String,java.lang.Throwable)>', '<android.util.Log: int e(java.lang.String,java.lang.String)>'], 'call_external_APIs': ['<android.os.storage.StorageVolume: java.lang.String semGetPath()>'], 'call_reflect_APIs': []}
com.sec.android.easyMover.json {'method': '<r6.b: int r0(android.content.Context)>', 'call_APIs': ['<android.util.Log: int e(java.lang.String,java.lang.String,java.lang.Throwable)>', '<android.util.Log: int e(java.lang.String,java.lang.String)>', '<android.content.Context: java.lang.Object getSystemService(java.lang.String)>'], 'call_external_APIs': ['<android.hardware.usb.UsbManager: int semGetDataRoleStatus()>'], 'call_reflect_APIs': []}
com.sec.android.easyMover.json {'method': '<r6.b: boolean Z(android.bluetooth.BluetoothAdapter)>', 'call_APIs': ['<android.util.Log: int e(java.lang.String,java.lang.String,java.lang.Throwable)>', '<android.util.Log: int e(java.lang.String,java.lang.String)>'], 'call_external_APIs': ['<android.bluetooth.BluetoothAdapter: boolean semIsBleEnabled()>'], 'call_reflect_APIs': []}
com.sec.android.easyMover.json {'method': '<r6.b: int v0()>', 'call_APIs': ['<android.util.Log: int e(java.lang.String,java.lang.String)>'], 'call_external_APIs': ['<android.os.Build$VERSION: int SEM_PLATFORM_INT>'], 'call_reflect_APIs': []}
com.sec.android.easyMover.json {'method': '<r6.b: java.lang.String k0(android.content.Context)>', 'call_APIs': ['<android.util.Log: int e(java.lang.String,java.lang.String,java.lang.Throwable)>', '<android.util.Log: int e(java.lang.String,java.lang.String)>'], 'call_external_APIs': ['<android.graphics.Typeface: java.lang.String semGetFontPathOfCurrentFontStyle(android.content.Context,int)>'], 'call_reflect_APIs': []}
com.sec.android.easyMover.json {'method': '<r6.b: boolean R(android.content.Context,int,java.lang.String,boolean)>', 'call_APIs': ['<android.util.Log: int e(java.lang.String,java.lang.String,java.lang.Throwable)>', '<android.util.Log: int e(java.lang.String,java.lang.String)>', '<android.content.Context: java.lang.Object getSystemService(java.lang.String)>'], 'call_external_APIs': ['<android.app.AppOpsManager: void semSetModeWriteSms(int,java.lang.String,int)>'], 'call_reflect_APIs': []}
com.sec.android.easyMover.json {'method': '<l8.c: void e()>', 'call_APIs': ['<android.content.pm.PackageManager: android.content.pm.PackageInstaller getPackageInstaller()>', '<android.content.pm.PackageInstaller$SessionParams: void setInstallReason(int)>', '<android.content.pm.PackageInstaller: int createSession(android.content.pm.PackageInstaller$SessionParams)>', '<android.content.pm.PackageInstaller$SessionParams: void setAppPackageName(java.lang.String)>', '<android.content.pm.PackageInstaller$SessionParams: void <init>(int)>', '<android.content.pm.PackageInstaller$SessionParams: void setInstallLocation(int)>', '<android.os.Build$VERSION: int SDK_INT>'], 'call_external_APIs': ['<android.content.pm.PackageInstaller$SessionParams: void semSetInstallFlagsSkipDexOptimization()>'], 'call_reflect_APIs': ['Landroid/content/pm/PackageInstaller$SessionParams;->setInstallerPackageName']}
com.sec.android.easyMover.json {'method': '<com.samsung.android.lib.eternal.provider.items.DisplayItem: java.lang.String getFontFileName(android.content.Context)>', 'call_APIs': [], 'call_external_APIs': ['<android.graphics.Typeface: java.lang.String semGetFontPathOfCurrentFontStyle(android.content.Context,int)>'], 'call_reflect_APIs': []}
com.sec.android.easyMover.json {'method': '<com.samsung.android.lib.eternal.provider.items.ConnectionsItem: com.samsung.android.lib.episode.Scene getValue(android.content.Context,java.lang.String)>', 'call_APIs': ['<android.provider.Settings$Secure: int getInt(android.content.ContentResolver,java.lang.String,int)>', '<android.nfc.NfcAdapter: android.nfc.NfcAdapter getDefaultAdapter(android.content.Context)>', '<android.provider.Settings$Secure: java.lang.String getString(android.content.ContentResolver,java.lang.String)>', '<android.provider.Settings$Global: int getInt(android.content.ContentResolver,java.lang.String,int)>', '<android.content.Context: android.content.ContentResolver getContentResolver()>', '<android.nfc.NfcAdapter: boolean isNdefPushEnabled()>'], 'call_external_APIs': ['<android.nfc.NfcAdapter: int semGetAdapterState()>'], 'call_reflect_APIs': []}
com.sec.android.easyMover.json {'method': '<r2.a: void s(java.util.Map,int,e8.c,j8.a)>', 'call_APIs': ['<android.os.SystemClock: long elapsedRealtime()>', '<android.os.Build$VERSION: int SDK_INT>'], 'call_external_APIs': ['<android.os.UserHandle: int semGetIdentifier()>'], 'call_reflect_APIs': []}
com.sec.android.easyMover.json {'method': '<r6.b: void g0(android.view.View)>', 'call_APIs': ['<android.util.Log: int e(java.lang.String,java.lang.String,java.lang.Throwable)>', '<android.util.Log: int d(java.lang.String,java.lang.String)>', '<android.util.Log: int e(java.lang.String,java.lang.String)>'], 'call_external_APIs': ['<android.widget.AbsListView: void semSetGoToTopEnabled(boolean)>'], 'call_reflect_APIs': []}
--------------------------------------------------------------------------------
com.vaultmicro.camerafi.live.json {'method': '<ff3: void e(int)>', 'call_APIs': [], 'call_external_APIs': ['<android.media.AudioSystem: int setPolicyParameters(java.lang.String)>'], 'call_reflect_APIs': []}
com.vaultmicro.camerafi.live.json {'method': '<ff3: void d(int)>', 'call_APIs': [], 'call_external_APIs': ['<android.media.AudioSystem: int setPolicyParameters(java.lang.String)>'], 'call_reflect_APIs': []}
--------------------------------------------------------------------------------
com.microsoft.appmanager.json {'method': '<com.samsung.android.sdk.mdx.windowslink.tips.JustInTips: boolean isSupported()>', 'call_APIs': [], 'call_external_APIs': ['<android.os.Build$VERSION: int SEM_PLATFORM_INT>'], 'call_reflect_APIs': []}
--------------------------------------------------------------------------------
"""




def _convert(s):
    s = re.sub(r'(\(.*?\)(.*?)|:(.*?))$', "", s)
    return re.sub(r'\$', '/', s)

def backtrack_nonsdk_interfaces():
    r = result_sets[2]
    
    non_sdk = dict()
    csv_file = 'test/veridex-linux/hiddenapi-flags.csv'
    for line in open(csv_file):
        seg = line.strip().split(',')
        api = _convert(seg[0])
        tags = seg[1:]
        if api in non_sdk:
            non_sdk[api].update(tags)
        else:
            non_sdk[api] = set(tags)

    # print(list(non_sdk.keys())[:10])

    block_types = {
        'total': 0,
        'public': 0,
        'unsupport': 0,
        'conditional': 0,
        'block': 0,
    }
    fn = f'reflect-{r}/reflect-{r}-total-api.txt'
    for u in _to_lines(fn):
        block_types['total'] += 1
        assert u in non_sdk
        if 'public-api' in non_sdk[u]:
            block_types['public'] += 1
        elif any(map(lambda t: t.startswith('max-target-'), non_sdk[u])):
            block_types['conditional'] += 1
        elif 'unsupported' in non_sdk[u]:
            block_types['unsupport'] += 1
        elif 'blocked' in non_sdk[u]:
            block_types['block'] += 1
        else:
            print(non_sdk[u])
            assert False
    print(r, block_types)
"""
output of fdroid:
---
fdroid {'total': 487, 'public': 12, 'unsupport': 295, 'conditional': 164, 'block': 16}
======================================================================================================
output of gplay:
---
gplay {'total': 1556, 'public': 35, 'unsupport': 924, 'conditional': 535, 'block': 62}
======================================================================================================
output of malware:
---
malware {'total': 230, 'public': 11, 'unsupport': 138, 'conditional': 70, 'block': 11}
"""




def verify_annot_removed_usages():
    annot_removed_apis = {
        "android.webkit.WebChromeClient->onReachedMaxAppCacheSize(long,long,android.webkit.WebStorage$QuotaUpdater)",
        "android.webkit.WebSettings->setAppCacheEnabled(boolean)",
        "android.webkit.WebSettings->setAppCacheMaxSize(long)",
        "android.webkit.WebSettings->setAppCachePath(java.lang.String)",
    }

    for r in result_sets:
        used_app_count = 0
        for fn in os.listdir(f'{r}_call_APIs/'):
            fn = f'{r}_call_APIs/{fn}'
            used = set(_to_lines(fn))
            if used.intersection(annot_removed_apis):
                used_app_count += 1
        print(r, used_app_count)



if __name__ == '__main__':
    find_extra_cutomized_apis()

    # backtrack_nonaal_apis()
    # backtrack_nonsdk_interfaces()

    # verify_annot_removed_usages()
