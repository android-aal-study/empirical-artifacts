# AOSP Statistics

This folder consists data that mentioned in the Research Scope section. It contains two files of `cloc` results, and two files of `ls` results. Both run on the directories of AOSP repo tree. To be specific, we run the following commands on the AOSP root `<ROOT>`:

+ To obtain `cloc-aosp.txt`, we run the command: `cloc <ROOT>`
+ To obtain `cloc-framework.txt`, we run the command: `cloc <ROOT>/frameworks/base`
+ To obtain `ls-kt-aosp.txt`, we run the command: `find <ROOT> -type f -name "*.kt"`
+ To obtain `ls-kt-framework.txt`, we run the command: `find <ROOT>/frameworks/base -type f -name "*.kt"`

It helps us count AOSP source files or `.kt` files, which helps us confirming research scope.

Example run of counting `.kt` file usages in the framework:

```bash
$ python .\analyze_frameworks_kotlin.py
frameworks/base/libs/WindowManager/Shell/src/com/android/wm/shell/pip/tv/TvPipKeepClearAlgorithm.kt
frameworks/base/libs/WindowManager/Shell/src/com/android/wm/shell/bubbles/BubbleDataRepository.kt
frameworks/base/libs/WindowManager/Shell/src/com/android/wm/shell/bubbles/storage/BubblePersistentRepository.kt
frameworks/base/libs/WindowManager/Shell/src/com/android/wm/shell/bubbles/storage/BubbleEntity.kt
frameworks/base/libs/WindowManager/Shell/src/com/android/wm/shell/bubbles/storage/BubbleVolatileRepository.kt
frameworks/base/libs/WindowManager/Shell/src/com/android/wm/shell/bubbles/storage/BubbleXmlHelper.kt
frameworks/base/libs/WindowManager/Shell/src/com/android/wm/shell/bubbles/StackEducationView.kt
frameworks/base/libs/WindowManager/Shell/src/com/android/wm/shell/bubbles/DismissView.kt
frameworks/base/libs/WindowManager/Shell/src/com/android/wm/shell/bubbles/RelativeTouchListener.kt
frameworks/base/libs/WindowManager/Shell/src/com/android/wm/shell/bubbles/ManageEducationView.kt
frameworks/base/libs/WindowManager/Shell/src/com/android/wm/shell/bubbles/BubbleOverflow.kt
frameworks/base/libs/WindowManager/Shell/src/com/android/wm/shell/animation/PhysicsAnimator.kt
frameworks/base/libs/WindowManager/Shell/src/com/android/wm/shell/animation/PhysicsAnimatorTestUtils.kt
frameworks/base/libs/WindowManager/Shell/src/com/android/wm/shell/animation/FloatProperties.kt
frameworks/base/libs/WindowManager/Shell/src/com/android/wm/shell/common/FloatingContentCoordinator.kt
frameworks/base/libs/WindowManager/Shell/src/com/android/wm/shell/common/magnetictarget/MagnetizedObject.kt
frameworks/base/samples/demo/haptic-assessment/src/com/example/android/hapticassessment/MainActivity.kt
-----
{'test': 537, 'system-app': 586, 'sdk-tool': 42, 'others': 17}
```
