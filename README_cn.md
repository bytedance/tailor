# Tailor
[![GitHub license](https://img.shields.io/badge/license-Apache--2.0-brightgreen.svg)](https://github.com/bytedance/tailor/blob/master/LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Android-brightgreen.svg)](https://developer.android.com)
[![API](https://img.shields.io/badge/api-14%2B-green)](https://developer.android.com/about/dashboards)

Tailor是西瓜Android团队开发的一款通用内存快照裁剪压缩工具，通过它可以在异常时直接dump出一个迷你内存快照。快照中没
有任何敏感信息，更重要的是文件非常小的同时数据也相对完整，非常适合离线分析OOM及其他类型异常的调查定位。

## Apps using Tailor
<img src="docs/xigua.png" width="100"/><img src="docs/douyin.png" width="100"/><img src="docs/huoshan.png" width="100"/><img src="docs/kaiyan.png" width="100"/>

## Get started
Step 1: Add the JitPack repository to your build file
```gradle
allprojects {
    repositories {
        maven { url 'https://jitpack.io' }
    }
}
```

Step 2: Add the dependency
```gradle
dependencies {
    implementation 'com.github.bytedance:tailor:1.0.9'
}
```

Step 3: Add code for simple usage
```Java
// 在异常回调里通过 Tailor 获取快照
if (e instanceof java.lang.OutOfMemoryError) {
    String path = Environment.getExternalStorageDirectory().getAbsolutePath() + File.separator + "mini.hprof";
    try {
        Tailor.dumpHprofData(path, true);
    } catch (IOException ex) {
        ex.printStackTrace();
    }
}
```

```Java
// 也可以直接对已经存在的hprof文件裁剪压缩
Tailor.cropHprofData(source, target, true);
```

Step 4: Upload data
```shell
## !!! 应用需自己实现数据上传或回捞
```

Step 5: Process data (Python version 3.5以上)
```shell
## 还原数据, target.hprof 可通过 Android Studio 分析，通过 MAT 还需要 hprof-conv 转换
python3 library/src/main/python/decode.py -i mini.hprof -o target.hprof
```

```shell
## 解析验证
python3 library/src/main/python/verify.py -i source.hprof
```

```shell
## 裁剪压缩
python3 library/src/main/python/encode.py -i source.hprof -o mini.hprof
```

## Extra
1. [Android Camera内存问题剖析](https://mp.weixin.qq.com/s/-oaN-bOqHDjN30UP1FMpgA)
2. [西瓜视频稳定性治理体系建设一：Tailor 原理及实践](https://mp.weixin.qq.com/s/DWOQ9MSTkKSCBFQjPswPIQ)
3. [西瓜视频稳定性治理体系建设二：Raphael 原理及实践](https://mp.weixin.qq.com/s/RF3m9_v5bYTYbwY-d1RloQ)


## Support
1. 在[GitHub issues](https://github.com/bytedance/tailor/issues)上交流
2. 邮件: <a href="mailto:shentianzhou.stz@gmail.com">shentianzhou.stz@gmail.com</a>
3. 微信: 429013449
<p align="left"><img src="docs/wechat.jpg" alt="Wechat group" width="320px"></p>

## License
~~~
Copyright (c) 2020 ByteDance Inc

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
~~~