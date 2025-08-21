package com.example.ticket_booking_manager_client.ui

import android.content.Intent
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.RecyclerView
import androidx.viewpager2.widget.ViewPager2
import com.example.ticket_booking_manager_client.MainActivity
import com.example.ticket_booking_manager_client.R
import com.example.ticket_booking_manager_client.data.AppPrefs
import com.google.android.material.button.MaterialButton
import com.google.android.material.tabs.TabLayout
import com.google.android.material.tabs.TabLayoutMediator
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.MainScope
import kotlinx.coroutines.launch

class OnboardingActivity : AppCompatActivity(), CoroutineScope by MainScope() {

    data class Slide(val imageRes: Int, val title: String, val subtitle: String)

    private val slides = listOf(
        Slide(R.drawable.ic_plane_big, "Fast Flights", "Search, compare and book flights in a tap."),
        Slide(R.drawable.ic_train_big, "Comfortable Trains", "Pick classes, times and onboard services."),
        Slide(R.drawable.ic_bus_big, "Affordable Buses", "Great routes and prices across the country.")
    )

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_onboarding)

        val pager = findViewById<ViewPager2>(R.id.pager)
        val tabs = findViewById<TabLayout>(R.id.tabs)
        val skip = findViewById<MaterialButton>(R.id.skipBtn)
        val getStarted = findViewById<MaterialButton>(R.id.getStartedBtn)

        pager.adapter = SlidesAdapter(slides)
        pager.setPageTransformer { page, position ->
            page.alpha = 0.2f + (1 - kotlin.math.abs(position)) * 0.8f
            page.scaleY = 0.9f + (1 - kotlin.math.abs(position)) * 0.1f
            page.translationX = -position * page.width * 0.2f
        }
        TabLayoutMediator(tabs, pager) { _, _ -> }.attach()

        skip.setOnClickListener { finishOnboarding() }
        getStarted.setOnClickListener { finishOnboarding() }
    }

    private fun finishOnboarding() {
        val prefs = AppPrefs(this)
        launch {
            prefs.setOnboarded(true)
            startActivity(Intent(this@OnboardingActivity, MainActivity::class.java))
            finish()
        }
    }

    private class SlidesAdapter(val data: List<Slide>) :
        RecyclerView.Adapter<SlidesAdapter.VH>() {

        class VH(view: View) : RecyclerView.ViewHolder(view) {
            val img: ImageView = view.findViewById(R.id.slideImage)
            val title: TextView = view.findViewById(R.id.slideTitle)
            val subtitle: TextView = view.findViewById(R.id.slideSubtitle)
        }

        override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): VH {
            val v = LayoutInflater.from(parent.context)
                .inflate(R.layout.item_onboarding_slide, parent, false)
            return VH(v)
        }

        override fun onBindViewHolder(holder: VH, position: Int) {
            val s = data[position]
            holder.img.setImageResource(s.imageRes)
            holder.title.text = s.title
            holder.subtitle.text = s.subtitle
        }

        override fun getItemCount() = data.size
    }
}
