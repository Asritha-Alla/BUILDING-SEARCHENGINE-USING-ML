from django.urls import path

from . import views

urlpatterns = [path("index.html", views.index, name="index"),
			path("AdminLogin.html", views.AdminLogin, name="AdminLogin"),
			path("AdminLoginAction", views.AdminLoginAction, name="AdminLoginAction"),
			path("ManagerLogin.html", views.ManagerLogin, name="ManagerLogin"),
			path("ManagerLoginAction", views.ManagerLoginAction, name="ManagerLoginAction"),
			path("Signup.html", views.Signup, name="Signup"),
			path("SignupAction", views.SignupAction, name="SignupAction"),	    	
			path("UserLogin.html", views.UserLogin, name="UserLogin"),
			path("UserLoginAction", views.UserLoginAction, name="UserLoginAction"),
			path("ViewUsers", views.ViewUsers, name="ViewUsers"),
			path("VerifyUser", views.VerifyUser, name="VerifyUser"),
			path("Train", views.Train, name="Train"),		
			path("UploadDataset.html", views.UploadDataset, name="UploadDataset"),
			path("UploadDatasetAction", views.UploadDatasetAction, name="UploadDatasetAction"),
			path("SearchQuery.html", views.SearchQuery, name="SearchQuery"),
			path("SearchQueryAction", views.SearchQueryAction, name="SearchQueryAction"),
]