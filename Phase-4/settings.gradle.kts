pluginManagement {
    repositories {
        google()
        maven { url = uri("https://maven.google.com") }
        mavenCentral()
        gradlePluginPortal()

        // Optional mirror (pick ONE if you need it):
        maven { url = uri("https://mirrors.cloud.tencent.com/repository/google") }
        // or
        // maven { url = uri("https://maven.aliyun.com/repository/google") }
    }
    plugins {
        id("com.android.application") version "8.6.1"
        id("org.jetbrains.kotlin.android") version "2.0.21"
    }
}

dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        maven { url = uri("https://maven.google.com") }
        mavenCentral()
        // (repeat the same mirror here if you added one above)
    }
}

rootProject.name = "Phase-4"
include(":app")
