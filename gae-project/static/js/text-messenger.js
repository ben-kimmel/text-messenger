/**
 * @fileoverview
 * Provides interactions for all pages in the UI.
 *
 * @author fisherds@gmail.com (Dave Fisher)
 */

/** namespace. */
var rh = rh || {};
rh.textmessenger = rh.textmessenger || {};

/** Shared JavaScript that is used on more than 1 page. */
rh.textmessenger.sharedInit = function() {
	// Dialog Polyfill for browsers that don't support the dialog tag.
	var dialogs = document.querySelectorAll('dialog');
	for (var i = 0; i < dialogs.length; i++) {
		// Using an old school style for loop since this for compatibility.
		var dialog = dialogs[i];
		if (!dialog.showModal) {
			dialogPolyfill.registerDialog(dialog);
		}
	}

	$(".close-parent-dialog").click(function() {
		var dialogEl = $(this).closest("dialog").get(0);
		dialogEl.close();
	});

	// Select elements
	// All getmdl-select elements need to get bigger to avoid getting cropped by the card.
	$(".getmdl-select").click(function() {
		let
		$optionsContainer = $(this).find(".mdl-menu__container");
		if ($optionsContainer.hasClass("is-visible")) {
			// is-visible means its about to go NOT visible.
			$(this).height("initial");
		} else {
			// not having is-visible means its about to BECOME visible.
			$(this).height($optionsContainer.height());
		}
	});
	// Makes sure the extra space is removed if a user clicks elsewhere in stead of making a selection.
	$(".getmdl-select input").blur(function() {
		setTimeout(function() {
			$(".getmdl-select").height("initial");
		}, 250);
	});
};

rh.textmessenger.accountInfoPageInit = function() {
	// No JS needed beyond the sharedInit.
};

rh.textmessenger.contactsPageInit = function() {
	// Insert contact - Create
	$("#add-contact-btn").click(function() {
		document.querySelector('#insert-contact-dialog').showModal();
		$("#insert-contact-dialog input[name=contact_entity_key]").val("");
		$("#insert-contact-dialog input[name=nickname]").val("");
		$("#insert-contact-dialog input[name=phone_number]").val("");
		$("#insert-contact-dialog input[name=real_first_name]").val("");
		$("#insert-contact-dialog input[name=real_last_name]").val("");
		$("#insert-contact-dialog input[name=email]").val("");
		$("#insert-contact-dialog input[name=other_info]").val("");
		$("#insert-contact-dialog .nickname-for-delete").val("");
		$("#insert-contact-dialog .entity-key-for-delete").val("");
		$("#insert-contact-dialog .mdl-dialog__title").html("Add contact");
		$("#insert-contact-dialog .delete-contact-btn").hide();
		$("#insert-contact-dialog button[type=submit]").html("Add");
	});

	// Insert contact - Edit
	$(".contact-card").click(function() {
		document.querySelector('#insert-contact-dialog').showModal();
		var entityKey = $(this).find(".entity-key").html();
		var nickname = $(this).find(".contact-nickname").html();
		var phoneNumber = $(this).find(".contact-phone").html();
		var firstName = $(this).find(".contact-first-name").html();
		var lastName = $(this).find(".contact-last-name").html();
		var email = $(this).find(".contact-email").html();
		var otherInfo = $(this).find(".contact-other").html();
		$("#insert-contact-dialog input[name=contact_entity_key]").val(entityKey);

		// Note that I had to use change the mdl way to get the input label to float up.
		// See: https://github.com/google/material-design-lite/issues/1287
		document.querySelector('#nickname-field').MaterialTextfield.change(nickname);
		document.querySelector('#phone-number-field').MaterialTextfield.change(phoneNumber);
		document.querySelector('#first-name-field').MaterialTextfield.change(firstName);
		document.querySelector('#last-name-field').MaterialTextfield.change(lastName);
		document.querySelector('#email-field').MaterialTextfield.change(email);
		document.querySelector('#other-info-field').MaterialTextfield.change(otherInfo);

		$("#insert-contact-dialog .nickname-for-delete").html(nickname);
		$("#insert-contact-dialog .entity-key-for-delete").html(entityKey);
		$("#insert-contact-dialog .mdl-dialog__title").html("Update contact info");
		$("#insert-contact-dialog .delete-contact-btn").show();
		$("#insert-contact-dialog button[type=submit]").html("Update");
	});

	// Related to the Delete Contact modal
	$(".delete-contact-btn").click(function() {
		document.querySelector('#insert-contact-dialog').close();
		document.querySelector('#delete-contact-dialog').showModal();
		var nickname = $(this).find(".nickname-for-delete").html();
		var entityKey = $(this).find(".entity-key-for-delete").html();
		$("#delete-contact-nickname").html(nickname);
		$("input[name=contact_to_delete_key]").val(entityKey);
	});
};

rh.textmessenger.listsPageInit = function() {
	// Insert List - Create
	$("#add-list-btn").click(function() {
		document.querySelector('#add-list-dialog').showModal();
	});

	// Attach an event listener to the modal
	$('#insert-list-modal').on('shown.bs.modal', function() {
		$("input[name='name']").focus();
	});

	// Insert List - Edit
	$(".list-card").click(function() {
		var listKey = $(this).find(".entity-key").html();
		window.location.replace("/list?list_key=" + listKey);
	});
};

rh.textmessenger.listPageInit = function() {
	// Edit list name
	$("#edit-list-name-btn").click(function() {
		document.querySelector('#edit-list-name-dialog').showModal();
	});
	// Close the list rename modal and update the page title.
	$("#done-editing-list-name").click(function() {
		var name = $("input[name=name]").val();
		$("#list-name").text(name);
		$("input[name=contact_list_name]").val(name);
	});

	// Related to Deleting a List
	$("#delete-list-btn").click(function() {
		document.querySelector("#delete-list-dialog").showModal();
	});

	// Moving a contact into or out of the list.
	$(".concise-contact-card").click(function() {
		$elem = $(this);
		var isInListBeforeClick = $elem.parents(".contacts-in-list").length > 0;
		var hasMovedClass = $elem.hasClass("moved-contact");
		var entityKey = $(this).find(".entity-key").html();
		contactKeysToAddString = $("input[name=contact_keys_to_add]").val();
		contactKeysToRemoveString = $("input[name=contact_keys_to_remove]").val();

		$elem.detach();
		if (isInListBeforeClick && hasMovedClass) {
			// Originally not in the list, clicked in, but about to go back to
			// original state of not in the list.
			$elem.appendTo(".contacts-not-in-list > .mdl-grid").removeClass("moved-contact");
			// Remove from the contact_keys_to_add list
			contactKeysToAddString = rh.textmessenger.toggleStringInList(contactKeysToAddString, entityKey);
		} else if (isInListBeforeClick && !hasMovedClass) {
			// Never been moved. Originally in the list. Getting removed.
			$elem.appendTo(".contacts-not-in-list > .mdl-grid").addClass("moved-contact");
			// Add to the contact_keys_to_remove list
			contactKeysToRemoveString = rh.textmessenger.toggleStringInList(contactKeysToRemoveString, entityKey);
		} else if (!isInListBeforeClick && hasMovedClass) {
			// Originally in the list, clicked out, but about to go back to
			// original state of in the list.
			$elem.appendTo(".contacts-in-list > .mdl-grid").removeClass("moved-contact");
			// Remove from the contact_keys_to_remove list
			contactKeysToRemoveString = rh.textmessenger.toggleStringInList(contactKeysToRemoveString, entityKey);
		} else if (!isInListBeforeClick && !hasMovedClass) {
			// Never been moved. Originally not in the list. Adding to the list (most common case).
			$elem.appendTo(".contacts-in-list > .mdl-grid").addClass("moved-contact");
			// Add to the contact_keys_to_remove list
			contactKeysToAddString = rh.textmessenger.toggleStringInList(contactKeysToAddString, entityKey);
		}
		$("input[name=contact_keys_to_add]").val(contactKeysToAddString);
		$("input[name=contact_keys_to_remove]").val(contactKeysToRemoveString);
	});
};

rh.textmessenger.textMessagesPageInit = function() {
	// Delete a text message event.
	$(".delete-text-message-event-btn").click(function() {
		document.querySelector('#delete-text-message-event-dialog').showModal();
		var messageBody = $(this).find(".message-body-for-delete").html();
		var entityKey = $(this).find(".entity-key-for-delete").html();
		$("#delete-text-message-event-body").html(messageBody);
		$("input[name=text_message_event_to_delete_key]").val(entityKey);
	});
};

rh.textmessenger.createTextMessagePageInit = function() {

	// Initialize the date picker widget.
	$('input[name=send_date_time]').bootstrapMaterialDatePicker({
		format : 'MM-DD-YYYY hh:mm A',
		shortTime : true
	});

	$("#attach-img-btn").click(function() {
		rh.textmessenger.triggerFileInput();
	});

	$("#remove-img-btn").click(function() {
		$(this).hide();
		$("#current-img").hide();
		$("input[name=original_blob_key]").val("").prop("disabled", true);
		$("#attach-img-btn").text("Attach image");
	});

	$("#img-input").change(function(event) {
		console.log("image file changed");
		$("#attach-img-btn").text("Image saved");
		let
		file = event.target.files[0];
		var data = {
			message : file.name + " has been saved",
			timeout : 4000,
			actionHandler : rh.textmessenger.triggerFileInput,
			actionText : "Edit"
		};
		document.querySelector('#snackbar-container').MaterialSnackbar.showSnackbar(data);
	});

	rh.textmessenger.triggerFileInput = function() {
		document.getElementById("img-input").click();
	};

	// Just before the form submits perform this action
	$("#create-text-message-event-form").submit(function() {
		// The getmdl-select elements send to the server what they display.
		// However we want the data-val sent to the server not the displayed info.
		var listKey = $("#to_list").attr("data-val");
		$("#to_list").val(listKey);
		var individualKey = $("#to_individual").attr("data-val");
		$("#to_individual").val(individualKey);
	});

	// WHEN radio buttons
	$("input[name=when_radio_group]").change(function() {
		if (this.id == "scheduled-radio") {
			$(".scheduled-picker").show();
			$("#send-btn").html("Schedule");
			// Observation: If it said Update originally it should really go back to Update not Schedule.
		} else if (this.id == "now-radio") {
			$(".scheduled-picker").hide();
			$("#send-btn").html("Send Now");
		}
	});

	// TO radio buttons
	$("input[name=to_radio_group]").change(function() {
		if (this.id == "list-radio") {
			$("#list-select").show();
			$("#individual-contact-select").hide();
		} else if (this.id == "individual-radio") {
			$("#list-select").hide();
			$("#individual-contact-select").show();
		} else if (this.id == "all-radio") {
			$("#list-select").hide();
			$("#individual-contact-select").hide();
		}
	});
};

rh.textmessenger.triggerFileInput = function() {
	document.getElementById("img-input").click();
};

/* Helper methods */
rh.textmessenger.toggleStringInList = function(stringList, stringToToggle) {
	if (stringList.indexOf(stringToToggle) > -1) {
		// Present. Remove it.
		var res = stringList.replace(stringToToggle, "");
		res = res.replace(",,", ",");
		var trim = res.replace(/(^,)|(,$)/g, "");
		// from
		// http://stackoverflow.com/questions/661305/how-can-i-trim-the-leading-and-trailing-comma-in-javascript
		return trim;
	} else {
		// Not present. Add it.
		if (stringList.length > 0) {
			return stringList + "," + stringToToggle;
		} else {
			return stringToToggle;
		}
	}
};

/* Main */
$(document).ready(function() {
	rh.textmessenger.sharedInit();
	rh.textmessenger.accountInfoPageInit();
	rh.textmessenger.contactsPageInit();
	rh.textmessenger.listsPageInit();
	rh.textmessenger.listPageInit();
	rh.textmessenger.textMessagesPageInit();
	rh.textmessenger.createTextMessagePageInit();
});
