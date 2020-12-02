package com.bytedance.demo;

import android.Manifest;
import android.content.pm.PackageManager;
import android.os.Build;
import android.os.Bundle;
import android.os.Debug;
import android.os.Environment;
import android.support.v7.app.AppCompatActivity;
import android.view.View;

import com.bytedance.tailor.Tailor;

import java.io.RandomAccessFile;

public class MainActivity extends AppCompatActivity implements View.OnClickListener{
    static final String DIRECTORY = Environment.getExternalStorageDirectory().getAbsolutePath();
    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        setContentView(R.layout.main);
        findViewById(R.id.btn).setOnClickListener(this);

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            if(!(checkSelfPermission(Manifest.permission.WRITE_EXTERNAL_STORAGE) == PackageManager.PERMISSION_GRANTED)){
                String[] permissions = {Manifest.permission.WRITE_EXTERNAL_STORAGE};
                requestPermissions(permissions, 101);
            }
        }
    }

    @Override
    public void onClick(View view) {
        tailor_for_file();
        tailor_for_hook();
    }

    void tailor_for_file() {
        try {
            String source = DIRECTORY + "/0.hprof";
            String target = DIRECTORY + "/1.hprof";
            Debug.dumpHprofData(source);
            System.err.println("TAILOR: isHprofValid = " + isHprofValid(source));
            if (isHprofValid(source)) {
                Tailor.cropHprofData(source, target, true);
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    void tailor_for_hook() {
        String target = DIRECTORY + "/2.hprof";
        try {
            Tailor.dumpHprofData(target, true);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    boolean isHprofValid(String path) {
        try {
            RandomAccessFile file = new RandomAccessFile(path, "r");
            file.seek(file.length() - 9);
            return file.readByte() == 0x2C;
        } catch (Throwable t) {
           return false;
        }
    }
}