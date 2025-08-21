package com.example.ticket_booking_manager_client.data.remote

import android.content.Context
import com.example.ticket_booking_manager_client.data.TokenStore
import kotlinx.coroutines.runBlocking
import okhttp3.Interceptor
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

object ApiClient {
    // For emulator to hit localhost Flask: http://10.0.2.2:5000
    private const val BASE_URL = "http://31.56.227.174:5000/"

    fun create(context: Context): ApiService {
        val tokenStore = TokenStore(context)

        val authInterceptor = Interceptor { chain ->
            val original = chain.request()
            val builder = original.newBuilder()

            val token = runBlocking { tokenStore.getTokenOnce() }
            if (!token.isNullOrBlank()) {
                // token may or may not include "Bearer " depending on backend return
                val headerValue = if (token.startsWith("Bearer ")) token else "Bearer $token"
                builder.header("Authorization", headerValue)
            }

            chain.proceed(builder.build())
        }

        val logging = HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BODY
        }

        val client = OkHttpClient.Builder()
            .addInterceptor(logging)
            .addInterceptor(authInterceptor)
            .build()

        return Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(client)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(ApiService::class.java)
    }
}
