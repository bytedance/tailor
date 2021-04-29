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

public class MainActivity extends AppCompatActivity implements View.OnClickListener{
    static final String DIRECTORY = Environment.getExternalStorageDirectory().getAbsolutePath();

    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        setContentView(R.layout.main);
        findViewById(R.id.btn).setOnClickListener(this);

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            if (!(checkSelfPermission(Manifest.permission.WRITE_EXTERNAL_STORAGE) == PackageManager.PERMISSION_GRANTED)) {
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
            long t = System.currentTimeMillis();
            Debug.dumpHprofData(source);
            System.err.println(">>>>>>>> tailor_for_file: " + (System.currentTimeMillis() - t));
            Tailor.cropHprofData(source, target, true);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    void tailor_for_hook() {
        String target = DIRECTORY + "/2.hprof";
        try {
            long t = System.currentTimeMillis();
            Tailor.dumpHprofData(target, false);
            System.err.println(">>>>>>>> tailor_for_hook: " + (System.currentTimeMillis() - t));
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}