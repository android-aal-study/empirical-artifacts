# RQ2

## Draw Venn4 Diagram

We draw Venn4 diagrams with `api_info.py`. It is like the one in the `rq1` folder, while only desired functions are included. Simply run the script to obtain all venn4 diagrams. The example diagram (API-level 33) used in the paper main content is as below:

![venn4-33](venn4-33.png)

It looks slightly different to the one that shown in our paper. This is because the draw function relies on an open-source module [pyvenn](https://github.com/LankyCyril/pyvenn). We made modification to it for better visual appearance. However, we cannot redistribute our modified source code to the pyvenn, as we have not use the GPLv3 license in our repository, which is the license adopted by pyvenn and doing so will violate the license term.

The large number of exclusive methods at API-level 28, as well as no shared fields or methods among the four AALs, is due to the fact that, under 28, the CSV list only contains non-public APIs.

## Other Findings

