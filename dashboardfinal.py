import tkinter as tk
from tkinter import ttk, messagebox, Frame, BOTH, LEFT, RIGHT, X, Y, HORIZONTAL
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from tkinter import font as tkfont
import seaborn as sns

sns.set_theme(style="whitegrid")

class PriceIntelligenceAdvisor:
    def __init__(self, root):
        self.root = root
        self.root.title("Price Intelligence Advisor - Flipkart Dashboard")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f5f5fa")

        # Apply custom style
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TButton', font=('Segoe UI', 10, 'bold'), padding=6, background='#3949ab', foreground='white')
        style.map('TButton', foreground=[('active', 'white')], background=[('active', '#5c6bc0')])
        style.configure('TCombobox', padding=5)

        self.custom_font = tkfont.Font(family="Segoe UI", size=10)
        self.title_font = tkfont.Font(family="Segoe UI", size=14, weight="bold")

        data_loaded = self.load_data()
        if not data_loaded:
            return

        self.filtered_df = self.df.copy()
        self.create_frames()
        self.create_header()
        self.create_sidebar()
        self.create_main_dashboard()
        self.create_footer()

    def create_footer(self):
        self.footer_frame = Frame(self.root, bg="#1a237e", height=30)
        self.footer_frame.pack(fill=X)
        footer_label = tk.Label(
            self.footer_frame,
            text="Price Intelligence Advisor Dashboard - Created for Data Visualization Analysis",
            font=("Segoe UI", 9),
            bg="#1a237e",
            fg="white"
        )
        footer_label.pack(pady=5)    
        
    def load_data(self):
        try:
            # Show a loading message in a separate window
            loading_window = tk.Toplevel(self.root)
            loading_window.title("Loading Data")
            loading_window.geometry("300x100")
            loading_window.transient(self.root)
            loading_window.grab_set()
            
            loading_label = tk.Label(loading_window, text="Loading dataset, please wait...", padx=20, pady=20)
            loading_label.pack()
            
            # Update the window to show the message
            loading_window.update()
            
            # Load the Flipkart dataset
            file_path = (r"flipkart_cleaned.csv")
            print(f"Attempting to load data from: {file_path}")
            self.df = pd.read_csv(file_path)
            
            # Update message
            loading_label.config(text="Processing data...")
            loading_window.update()
            
            # Clean and preprocess data
            preprocess_success = self.preprocess_data()
            
            # Close the loading window
            loading_window.destroy()
            
            return preprocess_success
        except Exception as e:
            print(f"Error loading dataset: {str(e)}")
            messagebox.showerror("Data Loading Error", f"Error loading dataset: {str(e)}")
            return False
    
    def preprocess_data(self):
        try:
            # Make a copy to avoid warnings
            self.df = self.df.copy()
            
            # Print column names for debugging
            print("Columns in the dataset:", self.df.columns.tolist())
            
            # Extract numeric price values and handle missing values
            self.df['retail_price'] = pd.to_numeric(self.df['retail_price'], errors='coerce')
            self.df['discounted_price'] = pd.to_numeric(self.df['discounted_price'], errors='coerce')
            
            # Remove rows with invalid prices
            self.df = self.df.dropna(subset=['retail_price'])
            
            # For products where discounted_price is missing, use retail_price
            self.df['discounted_price'] = self.df['discounted_price'].fillna(self.df['retail_price'])
            
            # Calculate discount percentage
            self.df['discount_percentage'] = ((self.df['retail_price'] - self.df['discounted_price']) / 
                                             self.df['retail_price'] * 100)
            
            # Replace negative or invalid discounts with 0
            self.df['discount_percentage'] = self.df['discount_percentage'].clip(lower=0)
            
            # Clean and convert ratings
            self.df['product_rating'] = self.df['product_rating'].astype(str).str.replace('stars', '').str.strip()
            self.df['rating_numeric'] = pd.to_numeric(self.df['product_rating'], errors='coerce')
            
            # Fill missing values without using inplace
            self.df = self.df.assign(rating_numeric=self.df['rating_numeric'].fillna(0))
            
            # Extract category from product_category_tree
            print("Extracting categories from product_category_tree...")
            
            # Function to extract the main category
            def extract_category(text):
                if pd.isna(text):
                    return "Uncategorized"
                try:
                    # Remove brackets and quotes
                    clean_text = str(text).replace('[', '').replace(']', '').replace('{', '').replace('}', '')
                    # Get the first category (before any ">>")
                    if '>>' in clean_text:
                        main_cat = clean_text.split('>>')[0].strip()
                    else:
                        main_cat = clean_text.strip()
                    # Remove any remaining quotes
                    main_cat = main_cat.replace('"', '').replace("'", '')
                    # Remove any "category:" or similar text
                    if ':' in main_cat:
                        main_cat = main_cat.split(':')[-1].strip()
                    return main_cat
                except Exception as e:
                    print(f"Error extracting category: {e}, text: {text[:50]}")
                    return "Uncategorized"
            
            # Apply the extraction function
            self.df['category'] = self.df['product_category_tree'].apply(extract_category)
            
            # Print some sample categories
            sample_categories = self.df['category'].sample(min(10, len(self.df))).tolist()
            print(f"Sample categories: {sample_categories}")
            
            # Get unique categories and count them
            all_categories = self.df['category'].value_counts()
            print(f"Found {len(all_categories)} unique categories")
            
            # Select top categories for better UI (categories with at least 10 products)
            top_categories = all_categories[all_categories >= 10].index.tolist()
            
            # If there are too few categories with 10+ products, just take the top 15
            if len(top_categories) < 5:
                top_categories = all_categories.nlargest(15).index.tolist()
            
            self.categories = sorted(top_categories[:15])  # Limit to 15 for dropdown
            
            # For debugging
            print(f"Processed {len(self.df)} rows with {len(self.categories)} categories")
            print(f"Categories: {self.categories}")
            
            # Initialize filtered_df
            self.filtered_df = self.df.copy()
            
            return True
        except Exception as e:
            print(f"Error preprocessing data: {str(e)}")
            return False
    
    def create_frames(self):
        try:
            # Check if root is destroyed
            if not self.root.winfo_exists():
                return
                
            # Header frame
            self.header_frame = Frame(self.root, bg="#1a237e", height=70)
            self.header_frame.pack(fill=X)
            
            # Main content frame
            self.main_frame = Frame(self.root, bg="#f0f0f0")
            self.main_frame.pack(fill=BOTH, expand=True)
            
            # Sidebar frame
            self.sidebar_frame = Frame(self.main_frame, bg="#e0e0e0", width=250)
            self.sidebar_frame.pack(side=LEFT, fill=Y)
            
            # Dashboard content frame
            self.dashboard_frame = Frame(self.main_frame, bg="#f5f5f5")
            self.dashboard_frame.pack(side=RIGHT, fill=BOTH, expand=True)
            
            # Footer frame
            self.footer_frame = Frame(self.root, bg="#1a237e", height=30)
            self.footer_frame.pack(fill=X)
        except Exception as e:
            print(f"Error creating frames: {str(e)}")
            return False
        return True
    
    def create_header(self):
        try:
            if not self.root.winfo_exists():
                return False
                
            # App title
            title_label = tk.Label(self.header_frame, 
                                text="Price Intelligence Advisor", 
                                font=("Arial", 18, "bold"), 
                                bg="#1a237e", 
                                fg="white")
            title_label.pack(side=LEFT, padx=20, pady=15)
            
            # Subtitle
            subtitle_label = tk.Label(self.header_frame, 
                                   text="Smart Pricing Insights from Flipkart Data", 
                                   font=("Arial", 12), 
                                   bg="#1a237e", 
                                   fg="white")
            subtitle_label.pack(side=LEFT, padx=10, pady=15)
            
            # Add search button on right side
            search_frame = Frame(self.header_frame, bg="#1a237e")
            search_frame.pack(side=RIGHT, padx=20, pady=10)
            
            self.search_entry = tk.Entry(search_frame, width=20, font=("Arial", 10))
            self.search_entry.pack(side=LEFT, padx=5)
            
            search_button = tk.Button(search_frame, 
                                  text="Search", 
                                  bg="#f0f0f0", 
                                  fg="#1a237e",
                                  font=("Arial", 10, "bold"),
                                  command=self.search_products)
            search_button.pack(side=LEFT)
            
            return True
        except Exception as e:
            print(f"Error creating header: {str(e)}")
            return False
    
    def create_sidebar(self):
        try:
            if not self.root.winfo_exists():
                return False
            
            # Add padding
            padding_frame = Frame(self.sidebar_frame, bg="#e0e0e0", height=20)
            padding_frame.pack(fill=X)
            
            # Create a label for the filters section
            filters_label = tk.Label(self.sidebar_frame, 
                                  text="Filters", 
                                  font=("Arial", 14, "bold"), 
                                  bg="#e0e0e0")
            filters_label.pack(pady=10)
            
            # Category filter
            category_frame = Frame(self.sidebar_frame, bg="#e0e0e0")
            category_frame.pack(fill=X, padx=10, pady=5)
            
            category_label = tk.Label(category_frame, 
                                   text="Category:", 
                                   font=("Arial", 10, "bold"), 
                                   bg="#e0e0e0")
            category_label.pack(anchor="w")
            
            self.category_var = tk.StringVar(value="All Categories")
            self.category_dropdown = ttk.Combobox(category_frame, 
                                              textvariable=self.category_var,
                                              values=["All Categories"] + list(self.categories))
            self.category_dropdown.pack(fill=X, pady=5)
            self.category_dropdown.bind("<<ComboboxSelected>>", self.filter_data)
            
            # Price range filter
            price_frame = Frame(self.sidebar_frame, bg="#e0e0e0")
            price_frame.pack(fill=X, padx=10, pady=5)
            
            price_label = tk.Label(price_frame, 
                                text="Price Range:", 
                                font=("Arial", 10, "bold"), 
                                bg="#e0e0e0")
            price_label.pack(anchor="w")
            
            price_slider_frame = Frame(price_frame, bg="#e0e0e0")
            price_slider_frame.pack(fill=X, pady=5)
            
            self.min_price = tk.IntVar(value=0)
            self.max_price = tk.IntVar(value=10000)
            
            self.min_price_scale = ttk.Scale(price_slider_frame, 
                                          from_=0, 
                                          to=10000, 
                                          orient=HORIZONTAL,
                                          variable=self.min_price,
                                          command=lambda x: self.update_price_labels())
            self.min_price_scale.pack(fill=X)
            
            self.max_price_scale = ttk.Scale(price_slider_frame, 
                                          from_=0, 
                                          to=10000, 
                                          orient=HORIZONTAL,
                                          variable=self.max_price,
                                          command=lambda x: self.update_price_labels())
            self.max_price_scale.pack(fill=X, pady=5)
            
            self.price_range_label = tk.Label(price_slider_frame, 
                                           text=f"₹{self.min_price.get()} - ₹{self.max_price.get()}", 
                                           bg="#e0e0e0")
            self.price_range_label.pack()
            
            # Rating filter
            rating_frame = Frame(self.sidebar_frame, bg="#e0e0e0")
            rating_frame.pack(fill=X, padx=10, pady=5)
            
            rating_label = tk.Label(rating_frame, 
                                 text="Minimum Rating:", 
                                 font=("Arial", 10, "bold"), 
                                 bg="#e0e0e0")
            rating_label.pack(anchor="w")
            
            self.rating_var = tk.DoubleVar(value=3.0)
            self.rating_scale = ttk.Scale(rating_frame, 
                                       from_=0, 
                                       to=5, 
                                       orient=HORIZONTAL,
                                       variable=self.rating_var,
                                       command=lambda x: self.update_rating_label())
            self.rating_scale.pack(fill=X)
            
            self.rating_value_label = tk.Label(rating_frame, 
                                            text=f"{self.rating_var.get():.1f} ★", 
                                            bg="#e0e0e0")
            self.rating_value_label.pack(pady=5)
            
            # Apply filters button
            apply_button = tk.Button(self.sidebar_frame, 
                                  text="Apply Filters", 
                                  bg="#1a237e", 
                                  fg="white",
                                  font=("Arial", 11, "bold"),
                                  command=self.filter_data)
            apply_button.pack(fill=X, padx=10, pady=10)
            
            # Add a profit calculator section
            separator = ttk.Separator(self.sidebar_frame, orient=HORIZONTAL)
            separator.pack(fill=X, padx=10, pady=10)
            
            profit_label = tk.Label(self.sidebar_frame, 
                                 text="Profit Calculator", 
                                 font=("Arial", 14, "bold"), 
                                 bg="#e0e0e0")
            profit_label.pack(pady=5)
            
            # MRP input
            mrp_frame = Frame(self.sidebar_frame, bg="#e0e0e0")
            mrp_frame.pack(fill=X, padx=10, pady=5)
            
            mrp_label = tk.Label(mrp_frame, 
                              text="MRP (₹):", 
                              font=("Arial", 10), 
                              bg="#e0e0e0")
            mrp_label.pack(anchor="w")
            
            self.mrp_entry = tk.Entry(mrp_frame)
            self.mrp_entry.pack(fill=X, pady=2)
            
            # Selling Price input
            sp_frame = Frame(self.sidebar_frame, bg="#e0e0e0")
            sp_frame.pack(fill=X, padx=10, pady=5)
            
            sp_label = tk.Label(sp_frame, 
                             text="Selling Price (₹):", 
                             font=("Arial", 10), 
                             bg="#e0e0e0")
            sp_label.pack(anchor="w")
            
            self.sp_entry = tk.Entry(sp_frame)
            self.sp_entry.pack(fill=X, pady=2)
            
            # Calculate button
            calc_button = tk.Button(self.sidebar_frame, 
                                 text="Calculate", 
                                 bg="#4caf50", 
                                 fg="white",
                                 font=("Arial", 11),
                                 command=self.calculate_profit)
            calc_button.pack(fill=X, padx=10, pady=5)
            
            # Profit result
            self.profit_result_frame = Frame(self.sidebar_frame, bg="#e0e0e0")
            self.profit_result_frame.pack(fill=X, padx=10, pady=5)
            
            self.profit_label = tk.Label(self.profit_result_frame, 
                                      text="", 
                                      font=("Arial", 10, "bold"), 
                                      bg="#e0e0e0")
            self.profit_label.pack(anchor="w")
            
            self.discount_label = tk.Label(self.profit_result_frame, 
                                        text="", 
                                        font=("Arial", 10), 
                                        bg="#e0e0e0")
            self.discount_label.pack(anchor="w")
            return True
        except Exception as e:
            print(f"Error creating sidebar: {str(e)}")
            return False
    
    def create_main_dashboard(self):
        try:
            if not self.root.winfo_exists():
                return False
                
            # Create tabs for different visualizations
            self.notebook = ttk.Notebook(self.dashboard_frame)
            self.notebook.pack(fill=BOTH, expand=True, padx=10, pady=10)
            
            # Create different tabs
            self.overview_tab = ttk.Frame(self.notebook)
            self.price_vs_rating_tab = ttk.Frame(self.notebook)
            self.price_distribution_tab = ttk.Frame(self.notebook)
            self.traffic_light_tab = ttk.Frame(self.notebook)
            
            self.notebook.add(self.overview_tab, text="Price Overview")
            self.notebook.add(self.price_vs_rating_tab, text="Price vs Rating")
            self.notebook.add(self.price_distribution_tab, text="Price Distribution")
            self.notebook.add(self.traffic_light_tab, text="Price Advisor")
            
            # Setup tab content
            self.create_overview_tab()
            self.create_price_vs_rating_tab()
            self.create_price_distribution_tab()
            self.create_traffic_light_tab()
            return True
        except Exception as e:
            print(f"Error creating main dashboard: {str(e)}")
            return False
    
    def create_overview_tab(self):
        try:
            if not self.root.winfo_exists():
                return False
                
            # Title
            title_label = tk.Label(self.overview_tab, 
                                text="Overview: Suggested Price Ranges by Category", 
                                font=("Arial", 14, "bold"), 
                                bg="white")
            title_label.pack(pady=10)
            
            # Create frame for chart
            self.overview_chart_frame = Frame(self.overview_tab, bg="white")
            self.overview_chart_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
            
            # Plot chart
            self.plot_overview_chart(self.overview_chart_frame)
            return True
        except Exception as e:
            print(f"Error creating overview tab: {str(e)}")
            return False
    
    def plot_overview_chart(self, chart_frame):
        try:
            # Create matplotlib figure if it doesn't exist
            if not hasattr(self, 'overview_fig') or not hasattr(self, 'overview_canvas'):
                self.overview_fig = Figure(figsize=(10, 6), dpi=100)
                self.overview_ax = self.overview_fig.add_subplot(111)
                
                # Create canvas
                self.overview_canvas = FigureCanvasTkAgg(self.overview_fig, master=chart_frame)
                self.overview_canvas.draw()
                self.overview_canvas.get_tk_widget().pack(fill=BOTH, expand=True)
            
            # Clear any previous chart
            self.overview_ax.clear()
            
            # Get filtered data
            if hasattr(self, 'filtered_df'):
                filtered_data = self.filtered_df.copy()
            else:
                filtered_data = self.df.copy()
            
            # Filter by category (if selected)
            if self.category_var.get() != "All Categories":
                filtered_data = filtered_data[filtered_data['category'] == self.category_var.get()]
            
            # Remove NaN values
            filtered_data = filtered_data.dropna(subset=['retail_price', 'discounted_price', 'category'])
            
            # If no data after filtering, show a message
            if len(filtered_data) == 0:
                self.overview_ax.text(0.5, 0.5, "No data available for the selected filters", 
                                   ha='center', va='center', fontsize=14)
                self.overview_fig.tight_layout()
                self.overview_canvas.draw()
                return True
            
            # Get top 10 categories by count if showing all categories
            if self.category_var.get() == "All Categories":
                category_count = filtered_data['category'].value_counts().head(10)
                top_categories = category_count.index.tolist()
                filtered_data = filtered_data[filtered_data['category'].isin(top_categories)]
            
            # Group by category
            category_price_data = filtered_data.groupby('category').agg({
                'retail_price': ['mean', 'min', 'max'],
                'discounted_price': 'mean'
            }).reset_index()
            
            # Sort by mean price for better visualization
            category_price_data = category_price_data.sort_values(('retail_price', 'mean'))
            
            # Reshape data for plotting
            categories = category_price_data['category'].values
            mean_prices = category_price_data[('retail_price', 'mean')].values
            min_prices = category_price_data[('retail_price', 'min')].values
            max_prices = category_price_data[('retail_price', 'max')].values
            discounted_prices = category_price_data[('discounted_price', 'mean')].values
            
            # Plot data
            x = np.arange(len(categories))
            width = 0.35
            
            # Plot mean retail price
            bars1 = self.overview_ax.bar(x, mean_prices, width, label='Retail Price', color='#4285F4')
            
            # Plot mean discounted price
            bars2 = self.overview_ax.bar(x + width, discounted_prices, width, label='Discounted Price', color='#DB4437')
            
            # Configure chart
            self.overview_ax.set_xlabel('Category')
            self.overview_ax.set_ylabel('Price (₹)')
            self.overview_ax.set_title('Price Comparison by Category')
            self.overview_ax.set_xticks(x + width / 2)
            self.overview_ax.set_xticklabels([cat[:15] + '...' if len(cat) > 15 else cat for cat in categories], 
                                          rotation=45, ha='right')
            self.overview_ax.legend()
            
            # Add price range annotations to bars
            for i, (min_p, max_p) in enumerate(zip(min_prices, max_prices)):
                self.overview_ax.annotate(f'₹{min_p:.0f} - ₹{max_p:.0f}',
                                       xy=(i, mean_prices[i]),
                                       xytext=(0, 5),
                                       textcoords="offset points",
                                       ha='center', va='bottom',
                                       fontsize=7,
                                       rotation=90)
            
            # Adjust layout
            self.overview_fig.tight_layout()
            self.overview_canvas.draw()
            return True
        except Exception as e:
            print(f"Error plotting overview chart: {str(e)}")
            return False
    
    def create_price_vs_rating_tab(self):
        try:
            if not self.root.winfo_exists():
                return False
                
            # Title
            title_label = tk.Label(self.price_vs_rating_tab, 
                                text="Price vs Rating Analysis", 
                                font=("Arial", 14, "bold"), 
                                bg="white")
            title_label.pack(pady=10)
            
            # Add information text
            info_text = "This scatter plot shows the relationship between product prices and ratings. " + \
                       "Each point represents a product, with the color indicating the discount percentage. " + \
                       "The trend line shows the overall correlation between price and rating."
            info_label = tk.Label(self.price_vs_rating_tab,
                               text=info_text,
                               font=("Arial", 10),
                               bg="white",
                               wraplength=800,
                               justify="left")
            info_label.pack(pady=(0, 10), padx=20)
            
            # Create frame for chart
            self.price_rating_chart_frame = Frame(self.price_vs_rating_tab, bg="white")
            self.price_rating_chart_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
            
            # Add a refresh button in case the chart doesn't load properly
            refresh_button = tk.Button(self.price_vs_rating_tab,
                                     text="Refresh Chart",
                                     bg="#1a237e",
                                     fg="white",
                                     command=self.refresh_price_vs_rating)
            refresh_button.pack(pady=10)
            
            # Plot the scatter plot
            self.plot_price_vs_rating(self.price_rating_chart_frame)
            return True
        except Exception as e:
            print(f"Error creating price vs rating tab: {str(e)}")
            return False
            
    def refresh_price_vs_rating(self):
        """Force refresh the price vs rating chart"""
        try:
            # Check if we have the chart frame
            if not hasattr(self, 'price_rating_chart_frame'):
                messagebox.showerror("Error", "Chart frame not initialized")
                return False
                
            # Clear existing chart
            if hasattr(self, 'price_rating_fig') and hasattr(self, 'price_rating_canvas'):
                # Remove existing canvas
                self.price_rating_canvas.get_tk_widget().pack_forget()
                plt.close(self.price_rating_fig)
                
                # Delete attributes
                del self.price_rating_fig
                del self.price_rating_canvas
                if hasattr(self, 'price_rating_cbar'):
                    del self.price_rating_cbar
            
            # Recreate the chart
            success = self.plot_price_vs_rating(self.price_rating_chart_frame)
            
            if success:
                messagebox.showinfo("Success", "Price vs Rating chart has been refreshed")
            else:
                messagebox.showerror("Error", "Failed to refresh the chart")
                
            return success
        except Exception as e:
            print(f"Error refreshing price vs rating chart: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to refresh: {str(e)}")
            return False
    
    def plot_price_vs_rating(self, chart_frame):
        try:
            # Create figure if it doesn't exist
            if not hasattr(self, 'price_rating_fig') or not hasattr(self, 'price_rating_canvas'):
                self.price_rating_fig = Figure(figsize=(10, 6), dpi=100)
                self.price_rating_ax = self.price_rating_fig.add_subplot(111)
                
                # Create canvas
                self.price_rating_canvas = FigureCanvasTkAgg(self.price_rating_fig, master=chart_frame)
                self.price_rating_canvas.get_tk_widget().pack(fill=BOTH, expand=True)
            else:
                # Clear any previous chart
                self.price_rating_ax.clear()
                
                # Clear any existing colorbars
                if hasattr(self, 'price_rating_cbar'):
                    try:
                        self.price_rating_cbar.remove()
                    except:
                        pass
            
            # Get filtered data
            if hasattr(self, 'filtered_df'):
                filtered_data = self.filtered_df.copy()
            else:
                filtered_data = self.df.copy()
            
            # Filter by price range and rating (just to be sure)
            min_price = self.min_price.get()
            max_price = self.max_price.get()
            min_rating = self.rating_var.get()
            
            filtered_data = filtered_data.dropna(subset=['retail_price', 'rating_numeric', 'discount_percentage'])
            filtered_data = filtered_data[
                (filtered_data['retail_price'] >= min_price) & 
                (filtered_data['retail_price'] <= max_price) &
                (filtered_data['rating_numeric'] >= min_rating)
            ]
            
            # If no data after filtering, show a message
            if len(filtered_data) == 0:
                self.price_rating_ax.text(0.5, 0.5, "No data available for the selected filters", 
                                       ha='center', va='center', fontsize=14)
                self.price_rating_fig.tight_layout()
                self.price_rating_canvas.draw()
                return True
            
            # Limit data points for better performance and visualization
            if len(filtered_data) > 500:
                filtered_data = filtered_data.sample(500, random_state=42)
            
            # Create scatter plot
            scatter = self.price_rating_ax.scatter(
                filtered_data['retail_price'],
                filtered_data['rating_numeric'],
                c=filtered_data['discount_percentage'],
                cmap='viridis',
                alpha=0.7,
                s=50
            )
            
            # Add a color bar
            try:
                # Create new colorbar
                self.price_rating_cbar = self.price_rating_fig.colorbar(scatter, ax=self.price_rating_ax)
                self.price_rating_cbar.set_label('Discount %')
            except Exception as e:
                print(f"Error with colorbar: {e}")
            
            # Add a trend line
            if len(filtered_data) > 1:  # Need at least 2 points for a line
                try:
                    # Calculate trend line
                    z = np.polyfit(filtered_data['retail_price'], filtered_data['rating_numeric'], 1)
                    p = np.poly1d(z)
                    
                    # Calculate points for the trend line
                    x_min = filtered_data['retail_price'].min()
                    x_max = filtered_data['retail_price'].max()
                    x_range = np.linspace(x_min, x_max, 100)
                    
                    # Plot trend line
                    self.price_rating_ax.plot(
                        x_range,
                        p(x_range),
                        "r--", 
                        linewidth=2,
                        alpha=0.8,
                        label=f'Trend: y = {z[0]:.6f}x + {z[1]:.2f}'
                    )
                    
                    # Calculate correlation coefficient
                    corr = filtered_data['retail_price'].corr(filtered_data['rating_numeric'])
                    corr_text = f"Correlation: {corr:.2f}"
                    
                    # Add annotation showing correlation
                    self.price_rating_ax.annotate(
                        corr_text,
                        xy=(0.05, 0.95),
                        xycoords='axes fraction',
                        fontsize=10,
                        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8)
                    )
                    
                    # Add legend showing the trend line equation
                    self.price_rating_ax.legend(loc='upper right')
                    
                except Exception as e:
                    print(f"Error adding trend line: {e}")
            
            # Configure chart
            self.price_rating_ax.set_xlabel('Retail Price (₹)')
            self.price_rating_ax.set_ylabel('Rating (0-5 stars)')
            self.price_rating_ax.set_title('Price vs Rating with Discount Visualization')
            
            # Set reasonable limits
            max_price_to_show = min(filtered_data['retail_price'].max() * 1.1, max_price)
            self.price_rating_ax.set_xlim(0, max_price_to_show)
            self.price_rating_ax.set_ylim(0, 5.5)
            
            # Add grid for better readability
            self.price_rating_ax.grid(True, linestyle='--', alpha=0.7)
            
            # Adjust layout and draw
            self.price_rating_fig.tight_layout()
            self.price_rating_canvas.draw()
            
            return True
        except Exception as e:
            print(f"Error plotting price vs rating chart: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def create_price_distribution_tab(self):
        try:
            if not self.root.winfo_exists():
                return False
                
            # Title
            title_label = tk.Label(self.price_distribution_tab, 
                                text="Price Distribution by Category", 
                                font=("Arial", 14, "bold"), 
                                bg="white")
            title_label.pack(pady=10)
            
            # Add category selector for this specific tab
            selector_frame = Frame(self.price_distribution_tab, bg="white")
            selector_frame.pack(fill=X, padx=10)
            
            category_label = tk.Label(selector_frame, 
                                   text="Select category:", 
                                   font=("Arial", 10), 
                                   bg="white")
            category_label.pack(side=LEFT, padx=5)
            
            self.category_dist_var = tk.StringVar(value="All Categories")
            category_dropdown = ttk.Combobox(selector_frame, 
                                          textvariable=self.category_dist_var,
                                          values=["All Categories"] + list(self.categories))
            category_dropdown.pack(side=LEFT, padx=5)
            category_dropdown.bind("<<ComboboxSelected>>", self.update_price_distribution)
            
            # Create frame for chart
            self.price_distribution_chart_frame = Frame(self.price_distribution_tab, bg="white")
            self.price_distribution_chart_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
            
            # Create matplotlib figure
            self.dist_fig = Figure(figsize=(10, 6), dpi=100)
            self.dist_ax = self.dist_fig.add_subplot(111)
            
            # Create canvas
            self.dist_canvas = FigureCanvasTkAgg(self.dist_fig, master=self.price_distribution_chart_frame)
            self.dist_canvas.draw()
            self.dist_canvas.get_tk_widget().pack(fill=BOTH, expand=True)
            
            # Initial plot
            self.update_price_distribution()
            return True
        except Exception as e:
            print(f"Error creating price distribution tab: {str(e)}")
            return False
    
    def update_price_distribution(self, event=None):
        try:
            if not hasattr(self, 'dist_ax') or not hasattr(self, 'dist_canvas'):
                return False
                
            # Clear previous chart
            self.dist_ax.clear()
            
            # Get selected categories
            selected_category = self.category_dist_var.get()
            
            # Filter data
            if hasattr(self, 'filtered_df'):
                filtered_df = self.filtered_df.copy()
            else:
                filtered_df = self.df.copy()
                
            # Further filter by the category selected in this tab
            if selected_category != "All Categories":
                filtered_df = filtered_df[filtered_df['category'] == selected_category]
            
            # Remove NaN values
            filtered_df = filtered_df.dropna(subset=['retail_price', 'category'])
            
            # If no data, show message
            if len(filtered_df) == 0:
                self.dist_ax.text(0.5, 0.5, "No data available for the selected filters", 
                                 ha='center', va='center', fontsize=14)
                self.dist_fig.tight_layout()
                self.dist_canvas.draw()
                return True
            
            # Set a price ceiling for better visualization (exclude outliers)
            try:
                price_ceiling = min(10000, filtered_df['retail_price'].quantile(0.95))
                plot_df = filtered_df[filtered_df['retail_price'] <= price_ceiling]
            except Exception as e:
                print(f"Error setting price ceiling: {e}")
                plot_df = filtered_df
            
            # Ensure we have data after filtering
            if len(plot_df) == 0:
                plot_df = filtered_df
            
            # Get categories to display
            selected_categories = [selected_category]
            if selected_category == "All Categories":
                # Limit to top 5 categories by count
                selected_categories = filtered_df['category'].value_counts().nlargest(5).index.tolist()
            
            # Color palette
            colors = plt.cm.tab10.colors
            
            # Create a histogram for each category
            for i, category in enumerate(selected_categories):
                category_df = plot_df[plot_df['category'] == category]
                if not category_df.empty:
                    self.dist_ax.hist(category_df['retail_price'], 
                                    bins=30, 
                                    alpha=0.5, 
                                    label=category if len(category) < 15 else category[:12] + '...',
                                    color=colors[i % len(colors)])
            
            # Add vertical line for average price
            mean_price = plot_df['retail_price'].mean()
            self.dist_ax.axvline(mean_price, color='red', linestyle='dashed', linewidth=1)
            
            # Get ylim safely
            ylim = self.dist_ax.get_ylim()
            if ylim[1] > 0:
                self.dist_ax.text(mean_price + 50, ylim[1] * 0.9, 
                               f'Avg: ₹{mean_price:.0f}', 
                               color='red')
            
            # Add chart labels
            self.dist_ax.set_xlabel('Price (₹)')
            self.dist_ax.set_ylabel('Number of Products')
            self.dist_ax.set_title('Price Distribution by Category')
            self.dist_ax.legend()
            self.dist_ax.grid(True, linestyle='--', alpha=0.7)
            
            # Update the canvas
            self.dist_fig.tight_layout()
            self.dist_canvas.draw()
            return True
        except Exception as e:
            print(f"Error updating price distribution: {str(e)}")
            return False
    
    def create_traffic_light_tab(self):
        # Title
        title_label = tk.Label(self.traffic_light_tab, 
                            text="Pricing Health Indicators", 
                            font=("Arial", 14, "bold"), 
                            bg="white")
        title_label.pack(pady=10)
        
        # Create frame for the traffic light indicators
        self.traffic_light_frame = Frame(self.traffic_light_tab, bg="white")
        self.traffic_light_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Create three sections for traffic light
        self.green_frame = Frame(self.traffic_light_frame, bg="white")
        self.green_frame.pack(fill=BOTH, expand=True, padx=10, pady=5)
        
        green_title = tk.Label(self.green_frame, 
                            text="🟢 Fair Pricing (Good value for money)", 
                            font=("Arial", 12, "bold"), 
                            fg="#2e7d32",
                            bg="white")
        green_title.pack(anchor='w')
        
        self.green_listbox = tk.Listbox(self.green_frame, 
                                     height=5, 
                                     font=("Arial", 10),
                                     selectbackground="#b9f6ca",
                                     selectforeground="black")
        self.green_listbox.pack(fill=BOTH, expand=True)
        
        self.yellow_frame = Frame(self.traffic_light_frame, bg="white")
        self.yellow_frame.pack(fill=BOTH, expand=True, padx=10, pady=5)
        
        yellow_title = tk.Label(self.yellow_frame, 
                             text="🟡 Underpriced (High-value products)", 
                             font=("Arial", 12, "bold"), 
                             fg="#ff8f00",
                             bg="white")
        yellow_title.pack(anchor='w')
        
        self.yellow_listbox = tk.Listbox(self.yellow_frame, 
                                      height=5, 
                                      font=("Arial", 10),
                                      selectbackground="#ffecb3",
                                      selectforeground="black")
        self.yellow_listbox.pack(fill=BOTH, expand=True)
        
        self.red_frame = Frame(self.traffic_light_frame, bg="white")
        self.red_frame.pack(fill=BOTH, expand=True, padx=10, pady=5)
        
        red_title = tk.Label(self.red_frame, 
                          text="🔴 Overpriced (Poor value for money)", 
                          font=("Arial", 12, "bold"), 
                          fg="#c62828",
                          bg="white")
        red_title.pack(anchor='w')
        
        self.red_listbox = tk.Listbox(self.red_frame, 
                                   height=5, 
                                   font=("Arial", 10),
                                   selectbackground="#ffcdd2",
                                   selectforeground="black")
        self.red_listbox.pack(fill=BOTH, expand=True)
        
        # Add detailed view button
        details_button = tk.Button(self.traffic_light_frame,
                                text="View Details of Selected Item",
                                bg="#1a237e",
                                fg="white",
                                command=self.show_product_details)
        details_button.pack(pady=10)
        
        # Populate the traffic light indicators
        self.update_traffic_lights()
    
    def update_traffic_lights(self):
        try:
            # Clear existing items
            self.green_listbox.delete(0, tk.END)
            self.yellow_listbox.delete(0, tk.END)
            self.red_listbox.delete(0, tk.END)
            
            # Get filtered data
            if hasattr(self, 'filtered_df'):
                filtered_data = self.filtered_df.copy()
            else:
                filtered_data = self.df.copy()
            
            # If no data, show message and return
            if len(filtered_data) == 0:
                self.green_listbox.insert(tk.END, "No data available for the selected filters")
                self.yellow_listbox.insert(tk.END, "No data available for the selected filters")
                self.red_listbox.insert(tk.END, "No data available for the selected filters")
                return True
            
            # Clean the data
            filtered_data = filtered_data.dropna(subset=['retail_price', 'discounted_price', 'rating_numeric'])
            
            # Ensure discounted_price is not zero to avoid division by zero
            filtered_data = filtered_data[filtered_data['discounted_price'] > 0]
            
            # If still no data after cleaning, show message and return
            if len(filtered_data) == 0:
                self.green_listbox.insert(tk.END, "No valid data available after cleaning")
                self.yellow_listbox.insert(tk.END, "No valid data available after cleaning")
                self.red_listbox.insert(tk.END, "No valid data available after cleaning")
                return True
            
            # Calculate value metrics safely
            try:
                # Price to value ratio (lower is better value)
                filtered_data['price_to_value'] = filtered_data['retail_price'] / (filtered_data['rating_numeric'].clip(lower=0.1) * 10)
                
                # Also calculate standard discount percentage for reference
                filtered_data['discount_pct'] = ((filtered_data['retail_price'] - filtered_data['discounted_price']) / 
                                                filtered_data['retail_price'] * 100).clip(lower=0)
            except Exception as e:
                print(f"Error calculating value score: {e}")
                return False
            
            # Define thresholds
            rating_threshold = 3.5
            price_value_threshold = filtered_data['price_to_value'].median()
            
            # Get the products for each category (with safeguards)
            try:
                # Fair pricing - good ratings and reasonable price-to-value
                fair_pricing = filtered_data[
                    (filtered_data['rating_numeric'] >= rating_threshold) & 
                    (filtered_data['price_to_value'] <= price_value_threshold * 1.2)
                ].sort_values('rating_numeric', ascending=False).head(10)
                
                # Underpriced - high ratings and very good price-to-value
                underpriced = filtered_data[
                    (filtered_data['rating_numeric'] >= rating_threshold) & 
                    (filtered_data['price_to_value'] < price_value_threshold * 0.6)
                ].sort_values('price_to_value').head(10)
                
                # Overpriced - low ratings or high price-to-value
                overpriced = filtered_data[
                    (filtered_data['rating_numeric'] < rating_threshold) | 
                    (filtered_data['price_to_value'] > price_value_threshold * 1.5)
                ].sort_values('price_to_value', ascending=False).head(10)
            except Exception as e:
                print(f"Error filtering products: {e}")
                # Fallback - just take some products from each rating range
                fair_pricing = filtered_data[filtered_data['rating_numeric'] >= 4].head(10)
                underpriced = filtered_data[(filtered_data['rating_numeric'] >= 3) & 
                                           (filtered_data['rating_numeric'] < 4)].head(10)
                overpriced = filtered_data[filtered_data['rating_numeric'] < 3].head(10)
            
            # Add items to each listbox
            # Green - Fair pricing
            for i, row in fair_pricing.iterrows():
                product_name = row['product_name'] if len(row['product_name']) < 45 else row['product_name'][:42] + '...'
                self.green_listbox.insert(tk.END, f"{product_name} | ₹{row['retail_price']:.0f} | {row['rating_numeric']:.1f}★ | {row['discount_pct']:.0f}% off")
            
            # Yellow - Underpriced (potential bargains)
            for i, row in underpriced.iterrows():
                product_name = row['product_name'] if len(row['product_name']) < 45 else row['product_name'][:42] + '...'
                self.yellow_listbox.insert(tk.END, f"{product_name} | ₹{row['retail_price']:.0f} | {row['rating_numeric']:.1f}★ | {row['discount_pct']:.0f}% off")
            
            # Red - Overpriced
            for i, row in overpriced.iterrows():
                product_name = row['product_name'] if len(row['product_name']) < 45 else row['product_name'][:42] + '...'
                self.red_listbox.insert(tk.END, f"{product_name} | ₹{row['retail_price']:.0f} | {row['rating_numeric']:.1f}★ | {row['discount_pct']:.0f}% off")
                
            return True
        except Exception as e:
            print(f"Error updating traffic lights: {str(e)}")
            return False
    
    def show_product_details(self):
        # Get the selected item
        selected_listbox = None
        selected_index = -1
        
        if self.green_listbox.curselection():
            selected_listbox = self.green_listbox
            selected_index = self.green_listbox.curselection()[0]
        elif self.yellow_listbox.curselection():
            selected_listbox = self.yellow_listbox
            selected_index = self.yellow_listbox.curselection()[0]
        elif self.red_listbox.curselection():
            selected_listbox = self.red_listbox
            selected_index = self.red_listbox.curselection()[0]
        
        if selected_listbox is None:
            messagebox.showinfo("Selection Required", "Please select a product to view details.")
            return
        
        # Get product name from the selected item
        selected_text = selected_listbox.get(selected_index)
        product_name = selected_text.split(" | ")[0]
        
        # Find the product in the dataframe
        product_rows = self.df[self.df['product_name'].str.contains(product_name[:30], regex=False)]
        
        if product_rows.empty:
            messagebox.showinfo("Product Not Found", "Product details could not be found.")
            return
        
        # Get the first matching product
        product = product_rows.iloc[0]
        
        # Create a popup window for product details
        details_window = tk.Toplevel(self.root)
        details_window.title("Product Details")
        details_window.geometry("600x400")
        details_window.configure(bg="white")
        
        # Product name
        name_label = tk.Label(details_window, 
                          text=product['product_name'], 
                          font=("Arial", 14, "bold"), 
                          wraplength=550,
                          bg="white")
        name_label.pack(fill=X, padx=20, pady=10)
        
        # Create a frame for product details
        details_frame = Frame(details_window, bg="white")
        details_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)
        
        # Create two columns
        left_frame = Frame(details_frame, bg="white")
        left_frame.pack(side=LEFT, fill=BOTH, expand=True)
        
        right_frame = Frame(details_frame, bg="white")
        right_frame.pack(side=RIGHT, fill=BOTH, expand=True)
        
        # Left column details
        tk.Label(left_frame, text="Category:", font=("Arial", 10, "bold"), bg="white", anchor="w").pack(fill=X)
        tk.Label(left_frame, text=product['category'], font=("Arial", 10), bg="white", anchor="w").pack(fill=X, pady=(0, 5))
        
        tk.Label(left_frame, text="MRP:", font=("Arial", 10, "bold"), bg="white", anchor="w").pack(fill=X)
        tk.Label(left_frame, text=product['discounted_price'], font=("Arial", 10), bg="white", anchor="w").pack(fill=X, pady=(0, 5))
        
        tk.Label(left_frame, text="Selling Price:", font=("Arial", 10, "bold"), bg="white", anchor="w").pack(fill=X)
        tk.Label(left_frame, text=product['retail_price'], font=("Arial", 10), bg="white", anchor="w").pack(fill=X, pady=(0, 5))
        
        tk.Label(left_frame, text="Discount:", font=("Arial", 10, "bold"), bg="white", anchor="w").pack(fill=X)
        tk.Label(left_frame, text=f"{product['discount_percentage']:.2f}%", font=("Arial", 10), bg="white", anchor="w").pack(fill=X, pady=(0, 5))
        
        # Right column details
        tk.Label(right_frame, text="Rating:", font=("Arial", 10, "bold"), bg="white", anchor="w").pack(fill=X)
        tk.Label(right_frame, text=f"{product['rating_numeric']} ({product.get('rating_count', 'N/A')} ratings)", 
              font=("Arial", 10), bg="white", anchor="w").pack(fill=X, pady=(0, 5))
        
        # Product description (if available)
        if 'description' in product and isinstance(product['description'], str):
            tk.Label(details_window, text="Description:", font=("Arial", 10, "bold"), bg="white", anchor="w").pack(fill=X, padx=20)
            
            desc_text = tk.Text(details_window, height=6, wrap=tk.WORD, font=("Arial", 10))
            desc_text.pack(fill=X, padx=20, pady=5)
            desc_text.insert(tk.END, product['description'])
            desc_text.config(state=tk.DISABLED)
        
        # Close button
        close_button = tk.Button(details_window, 
                              text="Close", 
                              bg="#1a237e", 
                              fg="white",
                              command=details_window.destroy)
        close_button.pack(pady=10)
    
    def create_footer(self):
        try:
            if not self.root.winfo_exists():
                return False
                
            # Footer text
            footer_label = tk.Label(self.footer_frame, 
                                  text="Price Intelligence Advisor Dashboard - Created for Data Visualization Analysis", 
                                  font=("Arial", 8), 
                                  bg="#1a237e", 
                                  fg="white")
            footer_label.pack(pady=5)
            return True
        except Exception as e:
            print(f"Error creating footer: {str(e)}")
            return False
    
    def update_price_labels(self):
        # Ensure min price is less than max price
        if self.min_price.get() > self.max_price.get():
            self.min_price.set(self.max_price.get())
        
        # Update the label
        self.price_range_label.config(text=f"₹{self.min_price.get()} - ₹{self.max_price.get()}")
    
    def update_rating_label(self):
        # Update the label
        self.rating_value_label.config(text=f"{self.rating_var.get():.1f} ★")
    
    def filter_data(self, event=None):
        try:
            # Print initial dataset size for debugging
            initial_count = len(self.df)
            print(f"Initial dataset has {initial_count} products")
            
            # Apply filters
            self.filtered_df = self.df.copy()
            
            # Category filter
            if self.category_var.get() != "All Categories":
                before_count = len(self.filtered_df)
                self.filtered_df = self.filtered_df[self.filtered_df['category'] == self.category_var.get()]
                after_count = len(self.filtered_df)
                print(f"Category filter: {before_count} -> {after_count}")
            
            # Price range filter
            before_count = len(self.filtered_df)
            self.filtered_df = self.filtered_df.dropna(subset=['retail_price'])
            self.filtered_df = self.filtered_df[
                (self.filtered_df['retail_price'] >= self.min_price.get()) & 
                (self.filtered_df['retail_price'] <= self.max_price.get())
            ]
            after_count = len(self.filtered_df)
            print(f"Price filter: {before_count} -> {after_count}")
            
            # Rating filter
            before_count = len(self.filtered_df)
            self.filtered_df = self.filtered_df.dropna(subset=['rating_numeric'])
            self.filtered_df = self.filtered_df[self.filtered_df['rating_numeric'] >= self.rating_var.get()]
            after_count = len(self.filtered_df)
            print(f"Rating filter: {before_count} -> {after_count}")
            
            # Update visualizations
            update_success = True
            
            # Update overview chart
            if hasattr(self, 'overview_chart_frame'):
                print("Updating overview chart...")
                try:
                    update_success = update_success and self.plot_overview_chart(self.overview_chart_frame)
                except Exception as e:
                    print(f"Error updating overview chart: {e}")
                    update_success = False
            
            # Update price vs rating chart
            if hasattr(self, 'price_rating_chart_frame'):
                print("Updating price vs rating chart...")
                try:
                    update_success = update_success and self.plot_price_vs_rating(self.price_rating_chart_frame)
                except Exception as e:
                    print(f"Error updating price vs rating chart: {e}")
                    update_success = False
            
            # Update price distribution
            if hasattr(self, 'dist_ax'):
                print("Updating price distribution...")
                try:
                    update_success = update_success and self.update_price_distribution()
                except Exception as e:
                    print(f"Error updating price distribution: {e}")
                    update_success = False
            
            # Update traffic lights
            if hasattr(self, 'green_listbox'):
                print("Updating traffic lights...")
                try:
                    update_success = update_success and self.update_traffic_lights()
                except Exception as e:
                    print(f"Error updating traffic lights: {e}")
                    update_success = False
                
            # Feedback to user
            filtered_count = len(self.filtered_df)
            print(f"Applied filters. Showing {filtered_count} products.")
            
            # Only show a message if we have data or if all the filters were applied manually (not on startup)
            if not update_success:
                messagebox.showerror("Update Error", "There was an error updating one or more visualizations.")
            elif event is not None and filtered_count == 0:
                messagebox.showinfo("Filter Results", "No products match your filter criteria. Try adjusting your filters.")
            
            return update_success
        except Exception as e:
            print(f"Error applying filters: {str(e)}")
            if event is not None:  # Only show error message if filter was triggered by user action
                messagebox.showerror("Filter Error", f"Error applying filters: {str(e)}")
            return False
    
    def calculate_profit(self):
        try:
            # Get input values
            mrp = float(self.mrp_entry.get())
            selling_price = float(self.sp_entry.get())
            
            # Calculate profit and discount
            profit = mrp - selling_price
            discount_percentage = (profit / mrp) * 100
            
            # Update labels
            self.profit_label.config(text=f"Profit: ₹{profit:.2f}")
            self.discount_label.config(text=f"Discount: {discount_percentage:.2f}%")
            
            # Add color based on discount percentage
            if discount_percentage < 10:
                self.profit_label.config(fg="#c62828")  # Red
            elif discount_percentage < 25:
                self.profit_label.config(fg="#ff8f00")  # Orange
            else:
                self.profit_label.config(fg="#2e7d32")  # Green
                
            # Give a business suggestion
            margin_percentage = (profit / selling_price) * 100
            
            if margin_percentage < 15:
                suggestion = "Consider increasing the selling price"
            elif discount_percentage > 40:
                suggestion = "Large discount may affect perceived value"
            else:
                suggestion = "Good profit margin"
                
            tk.Label(self.profit_result_frame, 
                  text=f"Margin: {margin_percentage:.2f}%", 
                  font=("Arial", 10), 
                  bg="#e0e0e0").pack(anchor="w")
                  
            tk.Label(self.profit_result_frame, 
                  text=suggestion, 
                  font=("Arial", 10, "italic"), 
                  bg="#e0e0e0").pack(anchor="w")
            
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numbers for MRP and Selling Price.")
    
    def search_products(self):
        """Search products by name"""
        try:
            # Get search term
            search_term = self.search_entry.get().strip()
            if not search_term:
                messagebox.showinfo("Search", "Please enter a search term")
                return
                
            # Filter data based on search term
            search_results = self.df[self.df['product_name'].str.contains(search_term, case=False, na=False)]
            
            # If no results found
            if len(search_results) == 0:
                messagebox.showinfo("Search Results", f"No products found matching '{search_term}'")
                return
                
            # Show results in a popup window
            results_window = tk.Toplevel(self.root)
            results_window.title(f"Search Results for '{search_term}'")
            results_window.geometry("800x600")
            results_window.configure(bg="white")
            
            # Create a frame for the results
            results_frame = Frame(results_window, bg="white")
            results_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
            
            # Create a title
            title_label = tk.Label(results_frame, 
                                text=f"Found {len(search_results)} products matching '{search_term}'", 
                                font=("Arial", 14, "bold"), 
                                bg="white")
            title_label.pack(pady=10)
            
            # Create scrollable frame for results
            scroll_frame = Frame(results_frame, bg="white")
            scroll_frame.pack(fill=BOTH, expand=True)
            
            # Add a scrollbar
            scrollbar = tk.Scrollbar(scroll_frame)
            scrollbar.pack(side=RIGHT, fill=Y)
            
            # Create a Treeview for displaying results
            columns = ("Product Name", "Category", "Price", "Rating")
            tree = ttk.Treeview(scroll_frame, columns=columns, show="headings", yscrollcommand=scrollbar.set)
            
            # Configure scrollbar
            scrollbar.config(command=tree.yview)
            
            # Set column headings
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=150)
            
            # Set column widths
            tree.column("Product Name", width=300)
            
            # Add data to the treeview
            for i, row in search_results.iterrows():
                price = f"₹{row['retail_price']:.0f}"
                rating = f"{row['rating_numeric']:.1f}★" if row['rating_numeric'] > 0 else "No rating"
                tree.insert("", "end", values=(row['product_name'], row['category'], price, rating))
            
            tree.pack(fill=BOTH, expand=True)
            
            # Add button to view details
            details_button = tk.Button(results_frame,
                                    text="View Details of Selected Product",
                                    bg="#1a237e",
                                    fg="white",
                                    command=lambda: self.show_search_product_details(tree, search_results))
            details_button.pack(pady=10)
            
            # Add event for double click
            tree.bind("<Double-1>", lambda event: self.show_search_product_details(tree, search_results))
            
        except Exception as e:
            print(f"Error searching products: {str(e)}")
            messagebox.showerror("Search Error", f"Error searching products: {str(e)}")
    
    def show_search_product_details(self, tree, search_results):
        """Show details of a selected search result"""
        # Get selected item
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showinfo("Selection Required", "Please select a product to view details")
            return
            
        # Get the index of the selected item
        selected_index = tree.index(selected_item[0])
        
        # Get product from search results
        product = search_results.iloc[selected_index]
        
        # Create a popup window for product details
        details_window = tk.Toplevel(self.root)
        details_window.title("Product Details")
        details_window.geometry("600x400")
        details_window.configure(bg="white")
        
        # Product name
        name_label = tk.Label(details_window, 
                          text=product['product_name'], 
                          font=("Arial", 14, "bold"), 
                          wraplength=550,
                          bg="white")
        name_label.pack(fill=X, padx=20, pady=10)
        
        # Create a frame for product details
        details_frame = Frame(details_window, bg="white")
        details_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)
        
        # Create two columns
        left_frame = Frame(details_frame, bg="white")
        left_frame.pack(side=LEFT, fill=BOTH, expand=True)
        
        right_frame = Frame(details_frame, bg="white")
        right_frame.pack(side=RIGHT, fill=BOTH, expand=True)
        
        # Left column details
        tk.Label(left_frame, text="Category:", font=("Arial", 10, "bold"), bg="white", anchor="w").pack(fill=X)
        tk.Label(left_frame, text=product['category'], font=("Arial", 10), bg="white", anchor="w").pack(fill=X, pady=(0, 5))
        
        tk.Label(left_frame, text="Retail Price:", font=("Arial", 10, "bold"), bg="white", anchor="w").pack(fill=X)
        tk.Label(left_frame, text=f"₹{product['retail_price']:.2f}", font=("Arial", 10), bg="white", anchor="w").pack(fill=X, pady=(0, 5))
        
        tk.Label(left_frame, text="Discounted Price:", font=("Arial", 10, "bold"), bg="white", anchor="w").pack(fill=X)
        tk.Label(left_frame, text=f"₹{product['discounted_price']:.2f}", font=("Arial", 10), bg="white", anchor="w").pack(fill=X, pady=(0, 5))
        
        tk.Label(left_frame, text="Discount:", font=("Arial", 10, "bold"), bg="white", anchor="w").pack(fill=X)
        tk.Label(left_frame, text=f"{product['discount_percentage']:.2f}%", font=("Arial", 10), bg="white", anchor="w").pack(fill=X, pady=(0, 5))
        
        # Right column details
        tk.Label(right_frame, text="Rating:", font=("Arial", 10, "bold"), bg="white", anchor="w").pack(fill=X)
        rating_text = f"{product['rating_numeric']:.1f} stars" if product['rating_numeric'] > 0 else "No rating"
        tk.Label(right_frame, text=rating_text, font=("Arial", 10), bg="white", anchor="w").pack(fill=X, pady=(0, 5))
        
        # Product description (if available)
        if 'description' in product and isinstance(product['description'], str) and len(product['description']) > 0:
            tk.Label(details_window, text="Description:", font=("Arial", 10, "bold"), bg="white", anchor="w").pack(fill=X, padx=20)
            
            desc_text = tk.Text(details_window, height=6, wrap=tk.WORD, font=("Arial", 10))
            desc_text.pack(fill=X, padx=20, pady=5)
            desc_text.insert(tk.END, product['description'])
            desc_text.config(state=tk.DISABLED)
        
        # Close button
        close_button = tk.Button(details_window, 
                              text="Close", 
                              bg="#1a237e", 
                              fg="white",
                              command=details_window.destroy)
        close_button.pack(pady=10)


def main():
    root = tk.Tk()
    try:
        app = PriceIntelligenceAdvisor(root)
        root.mainloop()
    except Exception as e:
        print(f"Application error: {str(e)}")
        if root.winfo_exists():
            root.destroy()

if __name__ == "__main__":
    main()