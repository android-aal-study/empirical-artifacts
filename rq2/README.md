# RQ2

## Draw Venn4 Diagram

We draw Venn4 diagrams with `api_info.py`. It is like the one in the `rq1` folder, while only desired functions are included. Simply run the script to obtain all venn4 diagrams. The example diagram (API-level 33) used in the paper main content is as below:

![venn4-33](venn4-33.png)

It looks slightly different to the one that shown in our paper. This is because the draw function relies on an open-source module [pyvenn](https://github.com/LankyCyril/pyvenn). We made modification to it for better visual appearance. However, we cannot redistribute our modified source code to the pyvenn, as we have not use the GPLv3 license in our repository, which is the license adopted by pyvenn and doing so will violate the license term.

The large number of exclusive methods at API-level 28, as well as no shared fields or methods among the four AALs, is due to the fact that, under 28, the CSV list only contains non-public APIs.

## Other Findings

The findings in RQ2 are central to `analyze.py` script. If you want to analyze the versions other than 33, you can pass other API-level as command line arguments.

### Obtaining Finding 3

The can be run by executing the `analyze_class_intersection4()` function in the `analyze.py` script. Example run:

```bash
$ python .\analyze.py 31
{'android.*': 3089, 'org.apache.http.*': 13, 'javax.microedition.khronos.*': 11} total: 3113
all shared fields from shared classes
all shared methods from shared classes

$ python .\analyze.py 32
{'android.*': 3095, 'org.apache.http.*': 13, 'javax.microedition.khronos.*': 11} total: 3119
all shared fields from shared classes
all shared methods from shared classes

$ python .\analyze.py 33
{'android.*': 3153, 'org.apache.http.*': 13, 'javax.microedition.khronos.*': 11} total: 3177
all shared fields from shared classes
all shared methods from shared classes
```

### Obtaining Finding 4

We run `analyze_csv_exclusive()` to find out the proportion of exclusive CSV fields/methods that belong to the exclusive CSV classes. Example run:

```bash
$ python .\analyze.py 31
123121 (0.8030276348314973) fields from exclusive classes
188453 (0.8854126535176328) methods from non-exclusive classes

$ python .\analyze.py 33
134062 (0.8068830199581096) fields from exclusive classes
204467 (0.8885349626494349) methods from non-exclusive classes
```

To draw sample from exclusive CSV classes, we un-comment the sampling block in the `analyze_csv_exclusive()` function. By running the function, we obtained the 379 sample classes in the `sample-379.xlsx` file. Then we manually tagged the sample, and obtained the `sample-379-labels.xlsx` file. After our authors discussion, we automated the final categorization process, which is the `analyze_csv_sampling()` function. The final output is:

```
{'hide': 74, 'remove': 2, 'access': 17, 'internal': 58, 'aidl': 90, 'proto': 16, 'hpp': 8, 'sysprop': 1, 'repackaged-jdk': 32, 'repackaged-other': 81}
```

### Obtaining Finding 5


