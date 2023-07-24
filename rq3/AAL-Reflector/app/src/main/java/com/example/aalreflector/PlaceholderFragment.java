package com.example.aalreflector;

import android.content.Context;
import android.content.res.AssetManager;
import android.os.Build;
import android.os.Bundle;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;

import androidx.annotation.NonNull;
import androidx.fragment.app.Fragment;
import androidx.lifecycle.ViewModelProvider;

import com.example.aalreflector.databinding.FragmentMainBinding;
import com.google.android.material.snackbar.Snackbar;

import org.apache.commons.io.FileUtils;
import org.apache.commons.io.IOUtils;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStream;
import java.lang.reflect.Constructor;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import ir.androidexception.datatable.model.DataTableHeader;
import ir.androidexception.datatable.model.DataTableRow;

public class PlaceholderFragment extends Fragment {
    private static final String TAG = "PlaceholderFragment";

    private static final String ARG_SECTION_NUMBER = "section_number";
    private static final String ARG_AAL_TYPE = "aal_type";

    private PageViewModel pageViewModel;
    private FragmentMainBinding binding;

    public static PlaceholderFragment newInstance(int index, String aalType) {
        PlaceholderFragment fragment = new PlaceholderFragment();
        Bundle bundle = new Bundle();
        bundle.putInt(ARG_SECTION_NUMBER, index);
        bundle.putString(ARG_AAL_TYPE, aalType);
        fragment.setArguments(bundle);
        return fragment;
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        pageViewModel = new ViewModelProvider(this).get(PageViewModel.class);

        int index = 1;
        if (getArguments() != null) {
            index = getArguments().getInt(ARG_SECTION_NUMBER);
        }
        pageViewModel.setIndex(index);

        String aalType = getArguments().getString(ARG_AAL_TYPE);
        pageViewModel.setAalType(aalType);

        Log.i(TAG, "created: sectionNumber=" + index + ",aalType=" + aalType);
    }

    @Override
    public View onCreateView(
            @NonNull LayoutInflater inflater, ViewGroup container,
            Bundle savedInstanceState) {

        binding = FragmentMainBinding.inflate(inflater, container, false);
        View root = binding.getRoot();

        final String aalType = pageViewModel.getAalType();
        final View snack = binding.snackbarPos;
        binding.buttonReflect.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                String msg = "reflect in " + aalType + " list";
                Snackbar.make(snack, msg, Snackbar.LENGTH_SHORT).show();

                ArrayList<DataTableRow> rows = new ArrayList<>();

                if("ALL".equals(aalType)) {
                    DataEntity data = loadAllData();
                    DataTableRow row = new DataTableRow.Builder()
                            .value("" + data.apiLevel)
                            .value("" + data.totalClass)
                            .value("" + data.totalField)
                            .value("" + data.totalMethod)
                            .build();
                    rows.add(row);
                }
                else {
                    for (DataEntity data : loadData(aalType)) {
                        DataTableRow row = new DataTableRow.Builder()
                                .value("" + data.apiLevel)
                                .value(data.getClassCell())
                                .value(data.getFieldCell())
                                .value(data.getMethodCell())
                                .build();
                        rows.add(row);
                    }
                }

                binding.dataTable.setRows(rows);
                binding.dataTable.inflate(getContext());
            }
        });

        DataTableHeader header = new DataTableHeader.Builder()
                .item("API-level", 1)
                .item("class", 1)
                .item("field", 1)
                .item("method", 1)
                .build();
        binding.dataTable.setHeader(header);
        binding.dataTable.inflate(getContext());

        return root;
    }


    List<DataEntity> loadData(String aalType) {
        List<DataEntity> dataEntityList = new ArrayList<>();
        AssetManager manager = getActivity().getAssets();

        //write to file
        try {
            int apiLevel = android.os.Build.VERSION.SDK_INT;
            Context context = getActivity().getApplicationContext();
            String outputPath = context.getFilesDir() + "/android-" + apiLevel + "/";
            File outputDir = new File(outputPath);
            if (!outputDir.exists()) {
                boolean success = outputDir.mkdir();
            }

            Log.i(TAG, "write to file: " + outputPath);

            for (String dir : manager.list("sublist")) {
                Log.i(TAG, "asset path: " + dir);
                int level = Integer.parseInt(dir.replace("android-", ""));
                //get the SDK version of the device

                if (level != apiLevel) {
                    DataEntity entity = new DataEntity(level, 0, 0, 0);
                    dataEntityList.add(entity);
                    continue;
                }

                /* reflecting classes */

                int classCount = 0;
                int totalClassCount = 0;

                String classAssetPath = "sublist/android-" + apiLevel + "/" + aalType + "-class.txt";
                String classWriterPath = outputPath + aalType + "_missing_classes.txt";

                try(FileWriter classWriter = new FileWriter(classWriterPath);
                            InputStream stream = manager.open(classAssetPath)) {
                    for (String line : IOUtils.readLines(stream, StandardCharsets.US_ASCII)) {
                        totalClassCount++;

                        Class<?> clazz = ReflectUtil.getClass(line);
                        if (clazz != null) {
                            classCount++;
                        } else {
                            Log.e(TAG, "class not found: " + line);
                            classWriter.write(line + "\n");
                        }
                    }
                }

                /* reflecting fields */

                int fieldCount = 0;
                int totalFieldCount = 0;

                String fieldAssetPath = "sublist/android-" + apiLevel + "/" + aalType + "-field.txt";
                String fieldWriterPath = outputPath + aalType + "_missing_fields.txt";

                try(FileWriter fieldWriter = new FileWriter(fieldWriterPath);
                            InputStream stream = manager.open(fieldAssetPath)) {
                    for (String line : IOUtils.readLines(stream, StandardCharsets.US_ASCII)) {
                        totalFieldCount++;

                        String[] seg = line.split("->");
                        String className = seg[0];
                        String name = seg[1];

                        Field field = ReflectUtil.getField(className, name);
                        if(field != null) {
                            fieldCount++;
                        }
                        else {
                            Log.e(TAG, "field not found: " + line);
                            fieldWriter.write(line + "\n");
                        }
                    }
                }

                /* reflecting methods */

                int methodCount = 0;
                int totalMethodCount = 0;

                String methodAssetPath = "sublist/android-" + apiLevel + "/" + aalType + "-method.txt";
                String methodWriterPath = outputPath + aalType + "_missing_methods.txt";

                try(FileWriter methodWriter = new FileWriter(methodWriterPath);
                            InputStream stream = manager.open(methodAssetPath)) {
                    for (String line : IOUtils.readLines(stream, StandardCharsets.US_ASCII)) {
                        totalMethodCount++;

                        Matcher m = Pattern.compile("(.*?)->(.*?)\\((.*?)\\)").matcher(line);
                        m.find();
                        String className = m.group(1);
                        String name = m.group(2);
                        String[] parameters;
                        if(m.group(3).isEmpty()) {
                            parameters = new String[0];
                        }
                        else {
                            parameters = m.group(3).split(",");
                        }

                        if("<clinit>".equals(name)) {
                            Class<?> clazz = ReflectUtil.getClass(className);
                            if(clazz != null) {
                                methodCount++;
                            }
                            else {
                                Log.e(TAG, "method not found: " + line);
                                methodWriter.write(line + "\n");
                            }
                        }
                        else if("<init>".equals(name)) {
                            Constructor<?> constructor = ReflectUtil.getConstructor(className, parameters);
                            if(constructor != null) {
                                methodCount++;
                            }
                            else {
                                Log.e(TAG, "method not found: " + line);
                                methodWriter.write(line + "\n");
                            }
                        }
                        else {
                            Method method = ReflectUtil.getMethod(className, name, parameters);
                            if(method != null) {
                                methodCount++;
                            }
                            else {
                                Log.e(TAG, "method not found: " + line);
                                methodWriter.write(line + "\n");
                            }
                        }
                    }
                }

                // dumping data
                DataEntity entity = new DataEntity(apiLevel, classCount, totalClassCount, fieldCount, totalFieldCount, methodCount, totalMethodCount);
                dataEntityList.add(entity);
            }
        } catch (IOException ex) {
            return new ArrayList<>();
        }

        return dataEntityList;
    }

    DataEntity loadAllData() {
        int apiLevel = android.os.Build.VERSION.SDK_INT;
        String outputPath = getContext().getFilesDir() + "/android-" + apiLevel;
        File outputDir = new File(outputPath);
        if (!outputDir.exists()) {
            outputDir.mkdir();
        }

        Set<Class<?>> allClasses = new HashSet<>();
        int fieldNumber = 0;
        int methodNumber = 0;
        try {
            AssetManager manager = getActivity().getAssets();

            String[] aalTypes = new String[]{"JAR", "XML", "TXT", "CSV"};
            for(String aalType: aalTypes) {
                String classAssetPath = "sublist/android-" + apiLevel + "/" + aalType + "-class.txt";
                try(InputStream stream = manager.open(classAssetPath)) {
                    for(String line : IOUtils.readLines(stream, StandardCharsets.US_ASCII)) {
                        Class<?> clazz = ReflectUtil.getClass(line);
                        if (clazz != null) {
                            allClasses.add(clazz);
                        }
                    }
                }
            }

            String classWriterPath = outputPath + "/all_classes.txt";
            try(FileWriter writer = new FileWriter(classWriterPath)) {
                for(Class<?> clazz: allClasses) {
                    writer.write(clazz.getName());
                    writer.write('\n');
                }
            }

            String fieldWriterPath = outputPath + "/all_fields.txt";
            try(FileWriter writer = new FileWriter(fieldWriterPath)) {
                for(Class<?> clazz: allClasses) {
                    for(Field field: clazz.getDeclaredFields()) {
                        fieldNumber++;
                        writer.write(field.toString());
                        writer.write('\n');
                    }
                }
            }

            String methodWriterPath = outputPath + "/all_methods.txt";
            try(FileWriter writer = new FileWriter(methodWriterPath)) {
                for(Class<?> clazz : allClasses) {
                    for(Method method: clazz.getDeclaredMethods()) {
                        methodNumber++;
                        writer.write(method.toString());
                        writer.write('\n');
                    }
                    for(Constructor<?> method: clazz.getDeclaredConstructors()) {
                        methodNumber++;
                        String line = method.toString().replace("(", ".<init>(");
                        writer.write(line);
                        writer.write('\n');
                    }
                }
            }

        } catch (IOException ignored) {
        }

        return new DataEntity(apiLevel, allClasses.size(), fieldNumber, methodNumber);
    }


    @Override
    public void onDestroyView() {
        super.onDestroyView();
        binding = null;
    }
}
